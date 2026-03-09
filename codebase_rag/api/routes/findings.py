"""Vulnerability finding API routes: fix generation, diff view, apply patch."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from loguru import logger

from ..models import ApplyFixResponse, FindingStatus, FixProposal
from ..state import project_store

router = APIRouter(prefix="/findings", tags=["Findings"])


@router.post("/{finding_id}/fix", response_model=FixProposal)
async def generate_fix(finding_id: str, project_id: str):
    """Generate an AI-powered fix proposal for a vulnerability finding."""
    state = project_store.get(project_id)
    if not state:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not state.report:
        raise HTTPException(status_code=404, detail="No scan report available.")

    finding = None
    for f in state.report.findings:
        if f.finding_id == finding_id:
            finding = f
            break
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found.")

    # Check if we already generated a fix
    if finding_id in state.fix_proposals:
        return state.fix_proposals[finding_id]

    try:
        from ...auto_scanner import AutoScanner
        from ...config import settings

        scanner = AutoScanner(
            host=settings.MEMGRAPH_HOST,
            port=settings.MEMGRAPH_PORT,
            username=settings.MEMGRAPH_USERNAME,
            password=settings.MEMGRAPH_PASSWORD,
            project_path=str(state.upload_dir),
            orchestrator_config=settings.active_orchestrator_config,
        )
        proposal = await scanner.generate_fix(finding)
        state.fix_proposals[finding_id] = proposal
        finding.status = FindingStatus.FIX_GENERATED
        finding.fix_available = True
        finding.fix_diff = proposal.unified_diff
        return proposal

    except Exception as e:
        logger.error(f"Fix generation failed for {finding_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Fix generation failed: {e}")


@router.get("/{finding_id}/diff")
async def get_diff(finding_id: str, project_id: str):
    """Get the unified diff for an already-generated fix proposal."""
    state = project_store.get(project_id)
    if not state:
        raise HTTPException(status_code=404, detail="Project not found.")

    proposal = state.fix_proposals.get(finding_id)
    if not proposal:
        raise HTTPException(
            status_code=404,
            detail="No fix proposal generated yet. Call POST /fix first.",
        )

    return {
        "finding_id": finding_id,
        "file_path": proposal.file_path,
        "original_code": proposal.original_code,
        "patched_code": proposal.patched_code,
        "unified_diff": proposal.unified_diff,
        "explanation": proposal.explanation,
    }


@router.post("/{finding_id}/apply", response_model=ApplyFixResponse)
async def apply_fix(finding_id: str, project_id: str):
    """Apply an approved fix to the actual source files."""
    state = project_store.get(project_id)
    if not state:
        raise HTTPException(status_code=404, detail="Project not found.")

    proposal = state.fix_proposals.get(finding_id)
    if not proposal:
        raise HTTPException(
            status_code=404,
            detail="No fix proposal found. Generate one first.",
        )

    try:
        from ...tools.file_editor import FileEditor

        editor = FileEditor(project_root=str(state.upload_dir))
        editor.replace_code_block(
            file_path=proposal.file_path,
            target_block=proposal.original_code,
            replacement_block=proposal.patched_code,
        )

        # Update finding status
        for f in state.report.findings if state.report else []:
            if f.finding_id == finding_id:
                f.status = FindingStatus.APPLIED
                break

        logger.success(f"Fix applied for finding {finding_id}")
        return ApplyFixResponse(
            finding_id=finding_id,
            status="applied",
            message="Fix successfully applied to the source file.",
        )

    except Exception as e:
        logger.error(f"Apply fix failed for {finding_id}: {e}")
        return ApplyFixResponse(
            finding_id=finding_id,
            status="failed",
            message=f"Failed to apply fix: {e}",
        )
