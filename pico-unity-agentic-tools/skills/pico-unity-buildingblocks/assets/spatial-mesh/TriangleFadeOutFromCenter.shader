Shader "Custom/TriangleFadeOutFromCenter"
{
    Properties
    {
        _Color ("Color", Color) = (1,1,1,0.5)
        _SecondColor ("Second Color", Color) = (0,1,0,1)
        _ScanningColor ("Scanning Color", Color) = (1,1,1,0.5)
        _WireColor ("Wire Color", Color) = (0,0,0,1)
        _StartTime ("Start Time", Float) = 0
        _ScaleDuration ("Scale Duration", Float) = 1.0
        _MaxScale ("Max Scale", Float) = 0.98
        _WireThickness ("Wire Thickness", Float) = 0.01
        _ColorExponent ("Alpha Exponent", Range(0, 30)) = 2.0 // controls the shape of the color falloff curve
        _ShapeExponent ("Shape Exponent", Range(0, 1)) = .2 // controls the shape of the scale falloff curve
        _DistanceExponent ("Distance Exponent", Range(0, 1)) = .5 // controls the shape of the scale falloff curve
        _AlphaAreaMin ("Alpha Area Min", Range(1, 5)) = 4.0
        _AlphaAreaMax ("Alpha Area Max", Range(1, 10)) = 10.0
        _DepthCutoff ("Depth Cutoff", Range(0, 1)) = 0.02 // fragments below this alpha do not write depth / are not shaded
    }

    SubShader
    {
        // Enter the opaque-side queue: render after opaque objects and before transparent objects.
        Tags
        {
            "RenderType"     = "TransparentCutout"
            "Queue"          = "AlphaTest"
            "RenderPipeline" = "UniversalPipeline"
            "IgnoreProjector"= "True"
        }

        // ------------------------------------------------------------
        // HLSL block shared by all Passes (vertex/geometry shaders + common declarations)
        // ------------------------------------------------------------
        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        // Global variables (set by script via Shader.SetGlobalVector, placed outside CBUFFER)
        float3 _TargetPosition;

        // Material properties (SRP Batcher requires them inside UnityPerMaterial)
        CBUFFER_START(UnityPerMaterial)
            float4 _Color;
            float4 _SecondColor;
            float4 _ScanningColor;
            float4 _WireColor;
            float  _StartTime;
            float  _ScaleDuration;
            float  _MaxScale;
            float  _WireThickness;
            float  _ColorExponent;
            float  _ShapeExponent;
            float  _DistanceExponent;
            float  _AlphaAreaMin;
            float  _AlphaAreaMax;
            float  _DepthCutoff;
        CBUFFER_END

        struct appdata
        {
            float4 vertex : POSITION;
            float4 color  : COLOR;
            UNITY_VERTEX_INPUT_INSTANCE_ID
        };

        struct v2g
        {
            float4 projectionSpaceVertex : SV_POSITION;
            float4 worldSpacePosition    : TEXCOORD1;
            float3 barycentric           : TEXCOORD2;
            UNITY_VERTEX_OUTPUT_STEREO
        };

        struct g2f
        {
            float4 projectionSpaceVertex : SV_POSITION;
            float4 worldSpacePosition    : TEXCOORD0;
            float3 barycentric           : TEXCOORD2;
            float  delta                 : TEXCOORD3;
            float  area                  : TEXCOORD4;
            UNITY_VERTEX_OUTPUT_STEREO
        };

        v2g vert (appdata v)
        {
            v2g o = (v2g)0;
            UNITY_SETUP_INSTANCE_ID(v);
            UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
            o.projectionSpaceVertex = TransformObjectToHClip(v.vertex.xyz);
            o.worldSpacePosition    = float4(TransformObjectToWorld(v.vertex.xyz), 1.0);
            return o;
        }

        float diracDelta(int a, int x) { return max(0, 1 - abs(x - a)); }

        [maxvertexcount(3)]
        void geom(triangle v2g i[3], inout TriangleStream<g2f> triangleStream)
        {
            float a = distance(i[0].worldSpacePosition.xyz, i[1].worldSpacePosition.xyz);
            float b = distance(i[1].worldSpacePosition.xyz, i[2].worldSpacePosition.xyz);
            float c = distance(i[2].worldSpacePosition.xyz, i[0].worldSpacePosition.xyz);
            float s = a + b + c;
            float area = pow(s * (s - a) * (s - b) * (s - c), 0.25);
            float3 worldCenter = (i[0].worldSpacePosition.xyz + i[1].worldSpacePosition.xyz + i[2].worldSpacePosition.xyz) / 3.0;
            float distanceToTarget = distance(worldCenter, _TargetPosition);
            float time  = _Time.y - _StartTime - distanceToTarget + _DistanceExponent;
            float scale = pow(saturate(time / _ScaleDuration), _ShapeExponent) * _MaxScale;

            [unroll]
            for (int j = 0; j < 3; ++j)
            {
                g2f o = (g2f)0;
                o.area = area;
                float3 offset       = i[j].worldSpacePosition.xyz - worldCenter;
                float3 scaledVertex = worldCenter + offset * scale;
                o.projectionSpaceVertex = TransformWorldToHClip(scaledVertex);
                o.worldSpacePosition    = float4(scaledVertex, 1.0);
                o.barycentric           = float3(diracDelta(0, j), diracDelta(1, j), diracDelta(2, j));
                o.delta                 = time;
                UNITY_TRANSFER_VERTEX_OUTPUT_STEREO(i[j], o);
                triangleStream.Append(o);
            }
            triangleStream.RestartStrip();
        }
        ENDHLSL

        // ============================================================
        // Pass 1: depth pre-pass. LightMode=SRPDefaultUnlit
        // In the URP forward loop, SRPDefaultUnlit is drawn before UniversalForward,
        // so this step first fills the depth buffer with the depth of the "frontmost layer".
        // ============================================================
        Pass
        {
            Name "DepthPrime"
            Tags { "LightMode" = "SRPDefaultUnlit" }

            ColorMask 0
            ZWrite On
            ZTest LEqual
            Cull Off

            HLSLPROGRAM
            #pragma target 4.0
            #pragma vertex vert
            #pragma geometry geom
            #pragma fragment fragDepth

            half4 fragDepth (g2f i) : SV_Target
            {
                // Decide whether to write depth solely by final visibility (alpha); faded-out regions are not written, avoiding "air walls".
                float len   = distance(i.worldSpacePosition.xyz, _TargetPosition);
                float alpha = smoothstep(_AlphaAreaMax, _AlphaAreaMin, len);
                clip(alpha - _DepthCutoff);
                return 0;
            }
            ENDHLSL
        }

        // ============================================================
        // Pass 2: color. LightMode=UniversalForward
        // Depth has already been filled by Pass 1; only the frontmost layer passes the ZTest → self-occlusion and cross-object occlusion hold.
        // Offset -1,-1 compensates for the slight depth difference caused by the geometry shader's recomputation, avoiding the whole block being culled.
        // ============================================================
        Pass
        {
            Name "Forward"
            Tags { "LightMode" = "UniversalForward" }

            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            ZTest LEqual
            Offset -1, -1
            Cull Off

            HLSLPROGRAM
            #pragma target 4.0
            #pragma vertex vert
            #pragma geometry geom
            #pragma fragment frag

            half4 frag (g2f i) : SV_Target
            {
                float alphaFactor = pow(i.delta, _ColorExponent);
                alphaFactor = saturate(alphaFactor);
                half4 color = lerp(_Color, _SecondColor, alphaFactor);
                half4 black = half4(0, 0, 0, 0);

                half4 wireframeColor = lerp(black, _WireColor, alphaFactor);
                float edgeFactor    = min(min(i.barycentric.x, i.barycentric.y), i.barycentric.z);
                float edgeThickness = (_WireThickness / i.area) / min(_MaxScale, 1.0);
                float wire          = smoothstep(edgeThickness - 0.01, edgeThickness, edgeFactor);

                float len = distance(i.worldSpacePosition.xyz, _TargetPosition);
                float t   = frac(0.5 * len - _Time.y);
                color.rgba += lerp(black, _ScanningColor, pow(t, 30.0));

                half4 finalColor = lerp(wireframeColor, color, wire);
                float alpha = smoothstep(_AlphaAreaMax, _AlphaAreaMin, len);
                finalColor.a *= alpha;

                clip(finalColor.a - _DepthCutoff); // same discard criterion as Pass 1
                return finalColor;
            }
            ENDHLSL
        }
    }

    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
