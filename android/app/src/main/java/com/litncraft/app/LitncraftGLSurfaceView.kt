package com.litncraft.app

import android.content.Context
import android.opengl.GLSurfaceView

class LitncraftGLSurfaceView(context: Context) : GLSurfaceView(context) {
    private val renderer: LitncraftRenderer

    init {
        setEGLContextClientVersion(2)
        renderer = LitncraftRenderer(context)
        setRenderer(renderer)
        renderMode = RENDERMODE_CONTINUOUSLY
    }
}
