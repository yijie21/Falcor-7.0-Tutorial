import falcor

def render_graph_WireframePass():
    g = RenderGraph("WireframePass")
    WireframePass = createPass("WireframePass")
    g.addPass(WireframePass, "WireframePass")
    g.markOutput("WireframePass.output")
    return g

WireframPass = render_graph_WireframePass()
try: m.addGraph(WireframPass)
except NameError: None