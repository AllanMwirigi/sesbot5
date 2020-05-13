package com.example.hp.sesbot5;

import android.content.Context;

import com.android.volley.*;
import com.android.volley.toolbox.*;

/**
 * Created by HP on 2/15/2018.
 */

public class VolleySingleton {

    private static VolleySingleton instance;
    private RequestQueue rq;
    private static Context contxt;

    private VolleySingleton(Context context)
    {
        this.contxt = context;
        rq = getRequestQueue();
    }

    public RequestQueue getRequestQueue()
    {
        if(rq == null)
            rq = Volley.newRequestQueue(contxt.getApplicationContext());

        return rq;
    }

    public static synchronized VolleySingleton getInstance(Context context)
    {
        if(instance == null)
            instance = new VolleySingleton(context);

        return instance;
    }

    public <T> void addToRequestQueue(Request<T> request)
    {
        rq.add(request);
    }
}
