from utils import hash_password, verify_password

print(verify_password("string", "$2b$12$66EZc3GTeVlSj2azSs4I6.8pchhyPUOEa0vvEynTlzsr/fyuvjU1C"))
print(hash_password("string"))
# $2b$12$wKp8nyItVMuAN1E2IMLJauZeibhvBtTxJei6xwkaDEU0Kjp9pOV5m
# $2b$12$TRuqyhGBNKpmLyLil2jTA.tzpziiW8pAay9xFX7Xhofn3jQEn6H8C