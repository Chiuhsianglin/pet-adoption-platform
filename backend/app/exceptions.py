"""
Custom Business Exceptions
自訂業務異常類別
"""
from typing import Optional


# Base Exception
class BusinessException(Exception):
    """業務邏輯異常基礎類別"""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# Resource Not Found Exceptions
class ResourceNotFoundError(BusinessException):
    """資源不存在異常"""
    pass


class ApplicationNotFoundError(ResourceNotFoundError):
    """領養申請不存在"""
    pass


class PetNotFoundError(ResourceNotFoundError):
    """寵物不存在"""
    pass


class UserNotFoundError(ResourceNotFoundError):
    """用戶不存在"""
    pass


class NotificationNotFoundError(ResourceNotFoundError):
    """通知不存在"""
    pass


class ChatRoomNotFoundError(ResourceNotFoundError):
    """聊天室不存在"""
    pass


class PostNotFoundError(ResourceNotFoundError):
    """貼文不存在"""
    pass


class CommentNotFoundError(ResourceNotFoundError):
    """留言不存在"""
    pass


class MessageNotFoundError(ResourceNotFoundError):
    """訊息不存在"""
    pass


# Permission Exceptions
class PermissionDeniedError(BusinessException):
    """權限不足異常"""
    pass


# Validation Exceptions
class ValidationError(BusinessException):
    """資料驗證異常"""
    pass


class DocumentsIncompleteError(ValidationError):
    """文件不完整"""
    pass


class InvalidStatusTransitionError(ValidationError):
    """無效的狀態轉換"""
    pass


class PetNotAvailableError(ValidationError):
    """寵物無法領養"""
    pass


class DuplicateApplicationError(ValidationError):
    """重複申請"""
    pass


class InvalidApplicationStatusError(ValidationError):
    """無效的申請狀態"""
    pass


# Business Logic Exceptions
class HomeVisitNotCompletedError(BusinessException):
    """家訪未完成"""
    pass


class ApplicationNotSubmittedError(BusinessException):
    """申請未提交"""
    pass


class ChatRoomAlreadyExistsError(BusinessException):
    """聊天室已存在"""
    pass


class PostAlreadyLikedError(BusinessException):
    """已按讚"""
    pass


class PostNotLikedError(BusinessException):
    """未按讚"""
    pass


# Authentication & Authorization Exceptions
class AuthenticationError(BusinessException):
    """認證異常基礎類別"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """無效的憑證（密碼錯誤、token 無效等）"""
    pass


class UserAlreadyExistsError(AuthenticationError):
    """用戶已存在"""
    pass


class AccountDeactivatedError(AuthenticationError):
    """帳號已停用"""
    pass


class EmailNotVerifiedError(AuthenticationError):
    """Email 未驗證"""
    pass


class TokenExpiredError(AuthenticationError):
    """Token 已過期"""
    pass


class TokenRevokedError(AuthenticationError):
    """Token 已被撤銷"""
    pass
