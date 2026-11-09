package com.opdpro.mobile

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ProgressBar
import android.widget.Toast
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar
    private lateinit var swipeRefresh: SwipeRefreshLayout
    private lateinit var connectionError: View
    private var uploadCallback: ValueCallback<Array<Uri>>? = null
    private val appHost = Uri.parse(BuildConfig.OPD_START_URL).host
    private var pageLoadFailed = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.rgb(17, 61, 49)
        window.navigationBarColor = Color.rgb(17, 61, 49)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.appWebView)
        progressBar = findViewById(R.id.pageProgress)
        swipeRefresh = findViewById(R.id.swipeRefresh)
        connectionError = findViewById(R.id.connectionError)
        swipeRefresh.setOnRefreshListener { webView.reload() }
        findViewById<View>(R.id.retryButton).setOnClickListener { webView.loadUrl(BuildConfig.OPD_START_URL) }
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            allowFileAccess = false
            allowContentAccess = true
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            userAgentString = "$userAgentString OPDProAndroidApp"
        }
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)

        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView, url: String?, favicon: android.graphics.Bitmap?) {
                pageLoadFailed = false
                connectionError.visibility = View.GONE
            }

            override fun onPageFinished(view: WebView, url: String?) {
                swipeRefresh.isRefreshing = false
                if (!pageLoadFailed) connectionError.visibility = View.GONE
            }

            override fun onReceivedError(
                view: WebView,
                request: WebResourceRequest,
                error: android.webkit.WebResourceError,
            ) {
                if (request.isForMainFrame) {
                    pageLoadFailed = true
                    progressBar.visibility = View.GONE
                    swipeRefresh.isRefreshing = false
                    connectionError.visibility = View.VISIBLE
                }
            }

            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val target = request.url
                if (target.scheme in listOf("http", "https") && target.host == appHost) return false
                return try {
                    startActivity(Intent(Intent.ACTION_VIEW, target))
                    true
                } catch (_: ActivityNotFoundException) {
                    true
                }
            }
        }
        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView, newProgress: Int) {
                progressBar.progress = newProgress
                progressBar.visibility = if (newProgress < 100) View.VISIBLE else View.GONE
                if (newProgress == 100) swipeRefresh.isRefreshing = false
            }

            override fun onShowFileChooser(
                view: WebView,
                callback: ValueCallback<Array<Uri>>,
                params: FileChooserParams,
            ): Boolean {
                uploadCallback?.onReceiveValue(null)
                uploadCallback = callback
                return try {
                    startActivityForResult(params.createIntent(), FILE_CHOOSER_REQUEST)
                    true
                } catch (_: ActivityNotFoundException) {
                    uploadCallback = null
                    false
                }
            }
        }
        webView.loadUrl(BuildConfig.OPD_START_URL)
    }

    @Deprecated("Deprecated by Android; retained for WebView file chooser results")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == FILE_CHOOSER_REQUEST) {
            val selectedFiles = WebChromeClient.FileChooserParams.parseResult(resultCode, data)
            uploadCallback?.onReceiveValue(selectedFiles)
            uploadCallback = null
            return
        }
        super.onActivityResult(requestCode, resultCode, data)
    }

    @Deprecated("Deprecated by Android; WebView owns browser history")
    override fun onBackPressed() {
        if (::webView.isInitialized && webView.canGoBack()) webView.goBack()
        else super.onBackPressed()
    }

    override fun onDestroy() {
        if (::webView.isInitialized) {
            webView.stopLoading()
            webView.destroy()
        }
        super.onDestroy()
    }

    companion object {
        private const val FILE_CHOOSER_REQUEST = 4102
    }
}
