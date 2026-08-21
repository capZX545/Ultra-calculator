package org.capzx545.ultracalculator;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

public class MainActivity extends Activity {
    private WebView web;
    private static final String ASSET_PREFIX = "file:///android_asset/";

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setAllowFileAccessFromFileURLs(true);
        s.setAllowUniversalAccessFromFileURLs(true);
        s.setCacheMode(WebSettings.LOAD_NO_CACHE);
        s.setMediaPlaybackRequiresUserGesture(false);
        if (Build.VERSION.SDK_INT >= 21) {
            s.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        }
        try {
            s.setOffscreenPreRaster(true);
        } catch (Exception ignored) {
        }
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                if (request == null || request.getUrl() == null) {
                    return super.shouldInterceptRequest(view, request);
                }
                WebResourceResponse served = serve(request.getUrl());
                return served != null ? served : super.shouldInterceptRequest(view, request);
            }

            @Override
            @SuppressWarnings("deprecation")
            public WebResourceResponse shouldInterceptRequest(WebView view, String url) {
                if (url == null) return super.shouldInterceptRequest(view, url);
                WebResourceResponse served = serve(Uri.parse(url));
                return served != null ? served : super.shouldInterceptRequest(view, url);
            }
        });
        web.loadUrl(ASSET_PREFIX + "www/index.html");
        setContentView(web);
    }

    private WebResourceResponse serve(Uri uri) {
        if (uri == null) return null;
        String url = uri.toString();
        int cut = url.indexOf('?');
        if (cut >= 0) url = url.substring(0, cut);
        String asset = null;
        if (url.startsWith(ASSET_PREFIX)) {
            asset = Uri.decode(url.substring(ASSET_PREFIX.length()));
        } else if (url.contains("/assets/www/")) {
            int i = url.indexOf("/assets/www/");
            asset = "www/" + Uri.decode(url.substring(i + "/assets/www/".length()));
        }
        if (asset == null || asset.isEmpty()) return null;
        if (asset.contains("..")) return null;
        try {
            InputStream in = getAssets().open(asset);
            String mime = mimeOf(asset);
            Map<String, String> headers = new HashMap<>();
            headers.put("Cache-Control", "no-store");
            headers.put("Access-Control-Allow-Origin", "*");
            if (Build.VERSION.SDK_INT >= 21) {
                return new WebResourceResponse(mime, "", 200, "OK", headers, in);
            }
            return new WebResourceResponse(mime, "", in);
        } catch (IOException e) {
            return null;
        }
    }

    private static String mimeOf(String path) {
        String p = path.toLowerCase();
        if (p.endsWith(".wasm")) return "application/wasm";
        if (p.endsWith(".js") || p.endsWith(".mjs")) return "application/javascript";
        if (p.endsWith(".json")) return "application/json";
        if (p.endsWith(".css")) return "text/css";
        if (p.endsWith(".html") || p.endsWith(".htm")) return "text/html";
        if (p.endsWith(".whl") || p.endsWith(".zip")) return "application/zip";
        if (p.endsWith(".png")) return "image/png";
        if (p.endsWith(".jpg") || p.endsWith(".jpeg")) return "image/jpeg";
        if (p.endsWith(".svg")) return "image/svg+xml";
        if (p.endsWith(".py") || p.endsWith(".txt")) return "text/plain";
        return "application/octet-stream";
    }

    @Override
    public void onBackPressed() {
        if (web != null && web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }
}
