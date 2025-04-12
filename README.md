# WatchFaceStudio2Android
三星的WatchFaceStudio转化为android studio工程，方便调整参数



# 附带apk重新签名的方式

```sh
# 先对齐
zipalign -v 4 app-unsigned.apk app-aligned.apk


# 签名
apksigner sign \
  --ks my-release-key.jks \
  --ks-key-alias my-alias \
  --out app-signed.apk \
  app-aligned.apk
```

> zipalign和apksigner在android sdk的build-tools目录下，macos在~/Library/Android/sdk