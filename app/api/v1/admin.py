from pathlib import Path
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.containers import AppContainer
from app.services.data_initializer import (
    DataInitializationError,
    DataInitializerService,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/initialize-data", status_code=status.HTTP_201_CREATED)
@inject
async def initialize_data(
    session: Annotated[AsyncSession, Depends(Provide[AppContainer.db.session])],
):
    try:
        # CSV 파일 경로 설정 (프로젝트 루트에 있는 파일)
        csv_file_path = (
            Path(__file__).parent.parent.parent.parent / "company_tag_sample.csv"
        )

        # 데이터 초기화 서비스
        initializer = DataInitializerService(session)

        # 데이터 초기화 실행
        result = await initializer.initialize_data_from_csv(csv_file_path)

        return {"success": True, "data": result}

    except DataInitializationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 초기화 중 예상치 못한 오류가 발생했습니다: {str(e)}",
        )


@router.get("/data-status")
@inject
async def check_data_status(
    session: Annotated[AsyncSession, Depends(Provide[AppContainer.db.session])],
):
    try:
        initializer = DataInitializerService(session)
        is_initialized = await initializer.is_data_already_initialized()

        return {
            "is_initialized": is_initialized,
            "message": "데이터가 이미 초기화되어 있습니다."
            if is_initialized
            else "데이터가 아직 초기화되지 않았습니다.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 상태 확인 중 오류가 발생했습니다: {str(e)}",
        )
