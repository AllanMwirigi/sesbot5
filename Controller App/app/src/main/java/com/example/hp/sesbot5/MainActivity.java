package com.example.hp.sesbot5;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.webkit.WebView;
import android.widget.Button;

import com.android.volley.AuthFailureError;
import com.android.volley.Request;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.JsonObjectRequest;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

public class MainActivity extends AppCompatActivity implements View.OnTouchListener{

    private String currentMotion, lastMotion;
//    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button btnForward = (Button)findViewById(R.id.btn_forward);
        Button btnLeft = (Button)findViewById(R.id.btn_left);
        Button btnRight = (Button)findViewById(R.id.btn_right);
        Button btnReverse = (Button)findViewById(R.id.btn_reverse);

//        webView = (WebView)findViewById(R.id.webview);
//        webView.getSettings();
//        webView.loadUrl("http://192.168.1.107:8080/video.mjpg");

        currentMotion ="S";
        lastMotion = "X";

        btnForward.setOnTouchListener(this);
        btnLeft.setOnTouchListener(this);
        btnRight.setOnTouchListener(this);
        btnReverse.setOnTouchListener(this);
    }

    public void sendCommand(final String command){
//        String url = "http://192.168.1.105:3000/post";  //node server on comp
        String url = "http://192.168.0.196:5000/postcommands";  //flask server on pi
//        Log.e("Command", command);
        JSONObject params = new JSONObject();
        try {
            params.put("command", command);
        } catch (JSONException e) {
            e.printStackTrace();
        }

//        JsonObjectRequest jRq = new JsonObjectRequest(Request.Method.POST, url, params,
//                null, null);

        JsonObjectRequest jRq = new JsonObjectRequest(Request.Method.POST, url, params,
                new Response.Listener<JSONObject>(){
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            Log.e("Server response", response.getString("response"));
                        } catch (JSONException e) {
                            Log.e("Parse error", e.getMessage());
                        }
                    }
                },
                new Response.ErrorListener(){
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Log.e("Post error", "Sth wrong");
                        error.printStackTrace();

                    }
                });

        VolleySingleton.getInstance(this).addToRequestQueue(jRq);
    }

    @Override
    public boolean onTouch(View view, MotionEvent motionEvent) {
        if(motionEvent.getActionMasked() == MotionEvent.ACTION_DOWN) {
            int id = view.getId();
            if(id == R.id.btn_forward){
                currentMotion = "F";
            }
            if(id == R.id.btn_left){
                currentMotion = "L";
            }
            if(id == R.id.btn_right){
                currentMotion = "R";
            }
            if(id == R.id.btn_reverse) {
                currentMotion = "B";
            }
        }

        if(motionEvent.getActionMasked() == MotionEvent.ACTION_UP){
            currentMotion = "S";
        }

        if(!currentMotion.equalsIgnoreCase(lastMotion)){
            lastMotion = currentMotion;
            Log.e("Command", currentMotion);
            sendCommand(currentMotion);
        }


        return true;
    }
}
