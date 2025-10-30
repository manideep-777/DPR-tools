"""
PDF Generation Routes - Task 16
Handles PDF generation from form data using Playwright
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from prisma import Prisma
from middleware.auth import get_current_user
from playwright.sync_api import sync_playwright
import os
import logging
from datetime import datetime
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter(prefix="/pdf", tags=["PDF Generation"])
logger = logging.getLogger(__name__)

@router.post("/generate/{form_id}")
async def generate_pdf(
    form_id: int,
    language: str = "english",
    template_type: str = "professional",
    current_user = Depends(get_current_user)
):
    """
    Generate PDF document from DPR form data using Playwright
    
    Args:
        form_id: ID of the form to generate PDF for
        language: Language for PDF (english/telugu)
        template_type: Template style (basic/professional/bank-ready)
        current_user: Authenticated user from JWT
    
    Returns:
        JSON with PDF URL and metadata
    """
    db = Prisma()
    await db.connect()
    
    try:
        # Step 1: Retrieve all data for PDF generation
        logger.info(f"Generating PDF for form {form_id} by user {current_user.id}")
        
        # Fetch complete form data with all relations
        form = await db.dprform.find_unique(
            where={"id": form_id},
            include={
                "user": True,
                "entrepreneurDetails": True,
                "businessDetails": True,
                "productDetails": True,
                "financialDetails": True,
                "revenueAssumptions": True,
                "costDetails": True,
                "staffingDetails": True,
                "timelineDetails": True,
                "generatedContents": True,
                "financialProjections": True,
                "financialSummary": True,
            }
        )
        
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        # Verify ownership
        if form.userId != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to generate PDF for this form")
        
        # Fetch matched schemes
        matched_schemes = await db.selectedscheme.find_many(
            where={"formId": form_id},
            include={"scheme": True}
        )
        
        # Step 2: Determine frontend URL for rendering
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        pdf_render_url = f"{frontend_url}/pdf/{form_id}"
        
        logger.info(f"Rendering PDF from URL: {pdf_render_url}")
        
        # Step 3: Generate PDF using Playwright
        pdf_filename = f"DPR_{form.businessName.replace(' ', '_')}_{form_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join("uploads", pdf_filename)
        
        # Define synchronous PDF generation function for thread pool
        def generate_pdf_sync():
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    context = browser.new_context(
                        viewport={"width": 1920, "height": 1080},
                        device_scale_factor=2
                    )
                    page = context.new_page()
                    
                    # Navigate to the preview page
                    page.goto(pdf_render_url, wait_until="networkidle", timeout=60000)
                    
                    # Wait for content to load
                    page.wait_for_selector("body", timeout=30000)
                    
                    # Optional: Wait a bit more for dynamic content
                    page.wait_for_timeout(2000)
                    
                    # Generate PDF
                    page.pdf(
                        path=pdf_path,
                        format="A4",
                        print_background=True,
                        margin={
                            "top": "20mm",
                            "right": "15mm",
                            "bottom": "20mm",
                            "left": "15mm"
                        },
                        prefer_css_page_size=False
                    )
                    
                    logger.info(f"PDF generated successfully: {pdf_path}")
                    
                except Exception as e:
                    logger.error(f"Error generating PDF with Playwright: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
                finally:
                    browser.close()
        
        # Run Playwright in thread pool to avoid Windows asyncio subprocess issues
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, generate_pdf_sync)
        
        # Step 4: Get PDF file information
        pdf_url = f"/uploads/{pdf_filename}"
        file_size = os.path.getsize(pdf_path)
        logger.info(f"PDF stored locally: {pdf_path}")
        
        # Step 5: Save PDF metadata to database
        pdf_document = await db.pdfdocument.create(
            data={
                "formId": form_id,
                "fileUrl": pdf_url,
                "fileName": pdf_filename,
                "fileSize": file_size,
                "language": language,
                "templateType": template_type,
                "downloadCount": 0
            }
        )
        
        logger.info(f"PDF metadata saved to database: ID {pdf_document.id}")
        
        # Step 6: Return response
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "PDF generated successfully",
                "data": {
                    "pdfId": pdf_document.id,
                    "pdfUrl": pdf_url,
                    "fileName": pdf_filename,
                    "fileSize": file_size,
                    "language": language,
                    "templateType": template_type,
                    "generatedAt": pdf_document.generatedAt.isoformat()
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in PDF generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        await db.disconnect()


@router.get("/{pdf_id}")
async def get_pdf_details(
    pdf_id: int,
    current_user = Depends(get_current_user)
):
    """
    Get PDF document details
    
    Args:
        pdf_id: ID of the PDF document
        current_user: Authenticated user from JWT
    
    Returns:
        PDF document details
    """
    db = Prisma()
    await db.connect()
    
    try:
        pdf_document = await db.pdfdocument.find_unique(
            where={"id": pdf_id},
            include={"form": True}
        )
        
        if not pdf_document:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        # Verify ownership
        if pdf_document.form.userId != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this PDF")
        
        # Increment download count
        await db.pdfdocument.update(
            where={"id": pdf_id},
            data={"downloadCount": pdf_document.downloadCount + 1}
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "id": pdf_document.id,
                    "formId": pdf_document.formId,
                    "businessName": pdf_document.form.businessName,
                    "pdfUrl": pdf_document.fileUrl,
                    "fileName": pdf_document.fileName,
                    "fileSize": pdf_document.fileSize,
                    "language": pdf_document.language,
                    "templateType": pdf_document.templateType,
                    "generatedAt": pdf_document.generatedAt.isoformat(),
                    "downloadCount": pdf_document.downloadCount + 1
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving PDF details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        await db.disconnect()


@router.get("/form/{form_id}/list")
async def list_form_pdfs(
    form_id: int,
    current_user = Depends(get_current_user)
):
    """
    List all PDFs generated for a specific form
    
    Args:
        form_id: ID of the form
        current_user: Authenticated user from JWT
    
    Returns:
        List of PDF documents for the form
    """
    db = Prisma()
    await db.connect()
    
    try:
        # Verify form ownership
        form = await db.dprform.find_unique(where={"id": form_id})
        
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        if form.userId != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this form")
        
        # Get all PDFs for this form
        pdfs = await db.pdfdocument.find_many(
            where={"formId": form_id},
            order={"generatedAt": "desc"}
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "formId": form_id,
                "businessName": form.businessName,
                "totalPdfs": len(pdfs),
                "pdfs": [
                    {
                        "id": pdf.id,
                        "pdfUrl": pdf.fileUrl,
                        "fileName": pdf.fileName,
                        "fileSize": pdf.fileSize,
                        "language": pdf.language,
                        "templateType": pdf.templateType,
                        "generatedAt": pdf.generatedAt.isoformat(),
                        "downloadCount": pdf.downloadCount
                    }
                    for pdf in pdfs
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing PDFs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        await db.disconnect()
