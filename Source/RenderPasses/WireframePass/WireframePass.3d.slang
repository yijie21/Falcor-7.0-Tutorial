import Scene.Raster;

cbuffer PerFrameCB
{
    float4 gColor;
};

VSOut vsMain(VSIn vIn)
{
    return defaultVS(vIn);
}

float4 psMain() : SV_Target
{
    return gColor;
}