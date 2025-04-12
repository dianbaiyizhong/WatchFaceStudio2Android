plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "${appId}"
    compileSdk = 34

    defaultConfig {
        applicationId = "${appId}"
        minSdk = 34
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

    }

    buildTypes {
        release {
            // TODO:Add your signingConfig here to build release builds
            isMinifyEnabled = true
            // Ensure shrink resources is false, to avoid potential for them
            // being removed.
            isShrinkResources = false

            signingConfig = signingConfigs.getByName("debug")
        }
    }

}


tasks.whenTaskAdded {
    if (this.name == "assembleRelease") {
        this.doLast {
            val outputDir = File(layout.buildDirectory.asFile.get(), "outputs/apk/release")
            val targetDir = File(outputDir, "renamed")
            targetDir.mkdirs()

            copy {
                from(outputDir)
                into(targetDir)
                include("*.apk")
                rename { _ ->
                    "${rootProject.name}_${android.defaultConfig.versionName}.apk"
                }
            }
        }
    }
}