plugins {
    id("com.android.application")
    id("kotlin-android")
    id("dev.flutter.flutter-gradle-plugin")
    id("com.google.gms.google-services")
}
// Apply the Google Services Gradle plugin to enable Firebase services

android {
    namespace = "com.vibe.trendy" // ✅ Must match your Firebase project
    compileSdk = 34
    ndkVersion = "27.0.12077973" // Optional: Explicit NDK version for stability

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = "11"
    }

    packaging {
        resources {
            // Pick first occurrence of any conflicting native libraries
            pickFirsts.add("**/libaosl.so")
            pickFirsts.add("**/libagora-*.so")
            pickFirsts.add("**/libc++_shared.so")

            // Exclude the specific conflicting library from agora-rtm package
            // Based on the exact paths from the error message
            excludes.add("**/jetified-agora-rtm-2.2.1/**/libaosl.so")
            excludes.add("**/jetified-aosl-1.2.13.1/**/libaosl.so")

            // Exclude duplicate metadata files
            excludes.add("META-INF/*.version")
            excludes.add("META-INF/LICENSE")
            excludes.add("META-INF/LICENSE.txt")
            excludes.add("META-INF/license.txt")
            excludes.add("META-INF/NOTICE")
            excludes.add("META-INF/NOTICE.txt")
            excludes.add("META-INF/notice.txt")
            excludes.add("META-INF/ASL2.0")
            excludes.add("META-INF/*.kotlin_module")
        }
    }

    defaultConfig {
        applicationId = "com.vibe.trendy" // ✅ Must match Firebase `google-services.json`
        minSdk = 21 // ✅ Updated to 21 as minimum required
        targetSdk = 34
        versionCode = flutter.versionCode
        versionName = flutter.versionName
        multiDexEnabled = true // ✅ Add this if you get Dex errors with Firebase
    }

    signingConfigs {
        create("release") {
            storeFile = file("keystore/trendy-release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: "your_keystore_password"
            keyAlias = System.getenv("KEY_ALIAS") ?: "trendy-key"
            keyPassword = System.getenv("KEY_PASSWORD") ?: "your_key_password"
        }
    }

    productFlavors {
        create("development") {
            dimension = "default"
            applicationIdSuffix = ".dev"
            versionNameSuffix = "-dev"
            buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000\"")
        }
        create("staging") {
            dimension = "default"
            applicationIdSuffix = ".staging"
            versionNameSuffix = "-staging"
            buildConfigField("String", "API_BASE_URL", "\"https://staging-api.trendy.com\"")
        }
        create("production") {
            dimension = "default"
            applicationIdSuffix = ""
            versionNameSuffix = ""
            buildConfigField("String", "API_BASE_URL", "\"https://api.trendy.com\"")
        }
    }

    buildTypes {
        getByName("debug") {
            isDebuggable = true
            isMinifyEnabled = false
            isShrinkResources = false
            // applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
        
        getByName("release") {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            isShrinkResources = true
            isDebuggable = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

flutter {
    source = "../.."
}