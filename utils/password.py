from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str):
    try:
        return pwd_context.verify(password, hashed_password)
    except Exception as e:
        print(e)
        return False

# def get_access_token_by_user_id(Authorize: AuthJWT,
#                                        db: Session,
#                                        user_id: str):

#     user = user_service.get_by_id(db, user_id)
#     user_claims = {
#         "role": str(user.staff_unit.id),
#         "iin": str(user.iin)
#     }
#     access_token = Authorize.create_access_token(
#         subject=str(user.id),
#         user_claims=user_claims,
#         expires_time=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN)
#     )
#     return access_token