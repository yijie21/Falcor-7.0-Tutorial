![](docs/images/wireframe.png)

# Falcor-7.0-Tutorial

This is a tutorial of how to use Falcor **7.0** to self-define a render pass. Although there is a turotial on writing shaders and define a render pass in the original github [repo](https://github.com/nvidiagameworks/falcor), the code in the original tutorial (markdown files) is not compatible with the newly updated version of Falcor. So I created this repo to rewrite the tutorial based on the newly updated Falcor API.

Specifically, this tutorial mainly tells about how to create a wireframe render pass like the picture above.

## Download & Install

#### Prequisites

Please follow the original repository to prepare needed prequisites.

#### Clone the repository

```bash
git clone --recursive https://github.com/NVIDIAGameWorks/Falcor.git
```

#### Setup and Build

Run the setup bash script in the terminal.

```
./setup_vs2022.bat
```

**[Important]** Before build the project, please change all the <TreatWarningAsError> in each `.vsxproj` file, otherwise the building process will fail. And there is a quick way of doing this: use `vscode` to open the folder `Falcor\build\windows-vs2022\Source` and search for `<TreatWarningAsError>true` and replace them all with `<TreatWarningAsError>false`.

After this operation, build this project in the terminal.

```
cmake --build build/windows-vs2022
```



## Create the WireframePass

#### Create the pass using the given tool

Run this command in the terminal and a new pass folder will be created automatically in `Falcor/Source/RenderPasses`.

```
./tools/make_new_render_pass.bat WireframePass
```

#### Coding the pass

**This part will give different code from the tutorial in the original repository, because we adapt to the new api and make some changes accordingly to make the WireframePass work.**

1. Create the shader file as `Falcor/Source/RenderPasses/WireframePass/WireframePass.3d.slang`

   ```hlsl
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
   ```

2. Create a namespace in `Falcor/Source/RenderPasses/WireframePass/WireframePass.cpp` to store the parameters commonly used in this script.

   ```c++
   namespace {
       const char kShaderFile[] = "RenderPasses/WireframePass/WireframePass.3d.slang";
   }
   ```

   Note: if the compiled program can not find the shader file, change the path to absolute path.

3. Add private variables to `Falcor/Source/RenderPasses/WireframePass/WireframePass.h`

   ```c++
   ref<Scene> mpScene;
   ref<Program> mpProgram;
   ref<GraphicsState> mpGraphicsState;
   ref<RasterizerState> mpRasterState;
   ref<ProgramVars> mpVars;
   ref<Fbo> mpFbo;
   ```

4. `WireframePass()`

   ```c++
   WireframePass::WireframePass(ref<Device> pDevice, const Properties& props) : RenderPass(pDevice) {
       RasterizerState::Desc wireframeDesc;
       wireframeDesc.setFillMode(RasterizerState::FillMode::Wireframe);
       wireframeDesc.setCullMode(RasterizerState::CullMode::None);
       mpRasterState = RasterizerState::create(wireframeDesc);
   
       mpGraphicsState = GraphicsState::create(mpDevice);
   
       mpFbo = Fbo::create(mpDevice);
   }
   ```

5. `reflect()`

   ```c++
   RenderPassReflection WireframePass::reflect(const CompileData& compileData)
   {
       // Define the required resources here
       RenderPassReflection reflector;
       reflector.addOutput("output", "Wireframe view texture");
       return reflector;
   }
   ```

6. `setScene()`

   ```c++
   void WireframePass::setScene(RenderContext* pRenderContext, const ref<Scene>& pScene)
   {
       mpScene = pScene;
   
       if (mpScene != nullptr) {
           // Create wireframe program
           ProgramDesc desc;
           desc.addShaderModules(mpScene->getShaderModules());
           desc.addShaderLibrary(kShaderFile).vsEntry("vsMain").psEntry("psMain");
           desc.addTypeConformances(mpScene->getTypeConformances());
   
           mpProgram = Program::create(mpDevice, desc, mpScene->getSceneDefines());
           mpGraphicsState->setProgram(mpProgram);
   
           mpVars = ProgramVars::create(mpDevice, mpProgram.get());
       }
   }
   ```

7. `execute()`

   ```c++
   void WireframePass::execute(RenderContext* pRenderContext, const RenderData& renderData)
   {
       auto pTex = renderData.getTexture("output");
       mpFbo->attachColorTarget(pTex, uint32_t(0));
       const float4 clearColor(0, 0, 0, 1);
       pRenderContext->clearFbo(mpFbo.get(), clearColor, 1.0f, 0, FboAttachmentType::All);
       mpGraphicsState->setFbo(mpFbo);
   
       if (mpScene) {
           mpVars->getRootVar()["PerFrameCB"]["gColor"] = float4(0, 1, 0, 1);
           mpScene->rasterize(pRenderContext, mpGraphicsState.get(), mpVars.get(), mpRasterState, mpRasterState);
       }
   }
   ```

8. Create the `WireframePass.py` for Falcor to loading the render graph in `Falcor/scripts/WireframePass.py`

   ```python
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
   ```

   

## Rebuild the project

Since a new pass has been added as a part of the source code, we need to `Setup and Build` again. Just follow the steps above.

## Run the WireframePass

1. Open `build\windows-vs2022\bin\Debug\Mogwai.exe` and hit `File->Loading Script`, select the `WireframePass.py` we just created.
2. Hit `File->Loading Scene`, select `media\Arcade\Arcade.pyscene`, and the wireframe renderpass will show up in the window.
