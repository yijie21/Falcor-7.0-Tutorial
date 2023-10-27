add_plugin(WireframePass)

target_sources(WireframePass PRIVATE
    WireframePass.cpp
    WireframePass.h
)

target_source_group(WireframePass "RenderPasses")
