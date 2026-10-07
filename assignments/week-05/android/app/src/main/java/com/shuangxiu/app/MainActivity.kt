package com.shuangxiu.app

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.webkit.PermissionRequest
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private var filePathCallback: ValueCallback<Array<Uri>>? = null
    private var cameraImageUri: Uri? = null

    private val fileChooserLauncher: ActivityResultLauncher<Intent> =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            val callback = filePathCallback
            filePathCallback = null
            if (callback == null) return@registerForActivityResult
            if (result.resultCode != Activity.RESULT_OK) {
                callback.onReceiveValue(null)
                return@registerForActivityResult
            }
            val data = result.data
            val uris: Array<Uri>? = when {
                data?.clipData != null ->
                    (0 until data.clipData!!.itemCount)
                        .map { data.clipData!!.getItemAt(it).uri }.toTypedArray()
                data?.data != null -> arrayOf(data.data!!)
                cameraImageUri != null -> arrayOf(cameraImageUri!!)
                else -> null
            }
            callback.onReceiveValue(uris)
        }

    private val cameraPermissionLauncher: ActivityResultLauncher<String> =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (!granted) Toast.makeText(this, "未授予相机权限，将无法拍照", Toast.LENGTH_SHORT).show()
        }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
            != PackageManager.PERMISSION_GRANTED
        ) {
            cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
        }

        webView = WebView(this)
        setContentView(webView)

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            mediaPlaybackRequiresUserGesture = false
            allowFileAccess = true
        }
        webView.webViewClient = WebViewClient()
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                callback: ValueCallback<Array<Uri>>?,
                params: FileChooserParams?
            ): Boolean {
                filePathCallback?.onReceiveValue(null)
                filePathCallback = callback

                val cameraIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
                cameraImageUri = try {
                    val file = File.createTempFile("shot", ".jpg", cacheDir)
                    FileProvider.getUriForFile(
                        this@MainActivity, "$packageName.fileprovider", file
                    )
                } catch (e: Exception) {
                    null
                }
                cameraImageUri?.let { cameraIntent.putExtra(MediaStore.EXTRA_OUTPUT, it) }

                val pickIntent = Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "image/*"
                }
                val chooser = Intent(Intent.ACTION_CHOOSER).apply {
                    putExtra(Intent.EXTRA_INTENT, pickIntent)
                    putExtra(Intent.EXTRA_TITLE, "选择产品图片")
                    putExtra(Intent.EXTRA_INITIAL_INTENTS, arrayOf(cameraIntent))
                }
                fileChooserLauncher.launch(chooser)
                return true
            }

            override fun onPermissionRequest(request: PermissionRequest?) {
                request?.grant(arrayOf(PermissionRequest.RESOURCE_VIDEO_CAPTURE))
            }
        }

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) webView.goBack() else finish()
            }
        })

        webView.loadUrl("https://shuangxiu-app.vercel.app")
    }
}
