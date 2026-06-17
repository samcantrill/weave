# Recipe Plugins

`weave` supports explicit trusted recipe loading through Python entry points.
The preferred entry point group is `weave.recipes`.


Plugin loading is trusted code execution. Import-time side effects and recipe
behavior belong to the installed project packages that provide those plugins.
