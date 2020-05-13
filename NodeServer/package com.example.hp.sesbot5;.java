package com.example.hp.sesbot5;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
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

public class MainActivity extends AppCompatActivity implements View.OnTouchListener, View.OnClickListener{

    private boolean botIsOn;
    private boolean botGoingForward;
    private boolean botGoingLeft;
    private boolean botGoingRight;
    private boolean botGoingReverse;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button btnIgnition = (Button)findViewById(R.id.btn_ignition);
        Button btnForward = (Button)findViewById(R.id.btn_forward);
        Button btnLeft = (Button)findViewById(R.id.btn_left);
        Button btnRight = (Button)findViewById(R.id.btn_right);
        Button btnReverse = (Button)findViewById(R.id.btn_reverse);
        botIsOn = false;
        botGoingForward = false;
        botGoingLeft = false;
        botGoingRight = false;
        botGoingReverse = false;

        btnIgnition.setOnClickListener(this);
        btnForward.setOnTouchListener(this);
        btnLeft.setOnTouchListener(this);
        btnRight.setOnTouchListener(this);
        btnReverse.setOnTouchListener(this);
    }

    public void sendCommand(final String command){
        String url = "http://192.168.1.105:3000/post";
//        String url = "http://192.168.0.170:3000/post";
//        Log.e("Command", command);
        JSONObject params = new JSONObject();
        try {
            params.put("command", command);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        JsonObjectRequest jRq = new JsonObjectRequest(Request.Method.POST, url, params,
                new Response.Listener<JSONObject>(){
                    @Override
                    public void onResponse(JSONObject response) {
//                        try {
//                            Log.e("Server response", response.getString(""));
//                        } catch (JSONException e) {
//                            Log.e("Parse error", e.getMessage());
//                        }
                        Log.e("Server response", "Success");

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
    public void onClick(View view) {
        Button b = (Button)findViewById(view.getId());
        if (view.getId() == R.id.btn_ignition){
            if(!botIsOn){
                botIsOn = true;
                b.setText("Stop");
            }
            else{
                sendCommand("stop");
                botIsOn = false;
                b.setText("Start");
            }
        }
    }

    @Override
    public boolean onTouch(View view, MotionEvent motionEvent) {
        if(botIsOn){
            if(motionEvent.getAction() == MotionEvent.ACTION_DOWN) {
                switch(view.getId()){
                    case R.id.btn_forward:
                        if(!botGoingForward){
                            sendCommand("forward");
                            botGoingForward = true;
                        }
                        break;
                    case R.id.btn_left:
                        if(!botGoingLeft){
                            sendCommand("left");
                            botGoingLeft = true;
                        }
                        break;
                    case R.id.btn_right:
                        if(!botGoingRight){
                            sendCommand("right");
                            botGoingRight = true;
                        }
                        break;
                    case R.id.btn_reverse:
                        if(!botGoingReverse){
                            sendCommand("reverse");
                            botGoingReverse = true;
                        }
                        break;
                }
            } else if (motionEvent.getAction() == MotionEvent.ACTION_UP) {
                switch(view.getId()){
                    case R.id.btn_forward:
                        if(botGoingForward){
                            sendCommand("forwardS");
                            botGoingForward = false;
                        }
                        break;
                    case R.id.btn_left:
                        if(botGoingLeft){
                            sendCommand("leftS");
                            botGoingLeft = false;
                        }
                        break;
                    case R.id.btn_right:
                        if(botGoingRight){
                            sendCommand("rightS");
                            botGoingRight = true;
                        }
                        break;
                    case R.id.btn_reverse:
                        if(botGoingReverse){
                            sendCommand("reverseS");
                            botGoingReverse = false;
                        }
                        break;
                }
            }
        }

        return true;
    }
}
