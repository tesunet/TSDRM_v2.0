$(document).ready(function () {
    var CellSize = new go.Size(50, 50);
    var colors = {
        blue: "#2a6dc0",
        orange: "#ea2857",
        green: "#1cc1bc",
        gray: "#5b5b5b",
        white: "#F5F5F5"
    }
    var $ = go.GraphObject.make;  // for conciseness in defining templates
    myDiagram =
        $(go.Diagram, "myDiagramDiv",  // must name or refer to the DIV HTML element
            {
                "LinkDrawn": showLinkLabel,  // this DiagramEvent listener is defined below
                "LinkRelinked": showLinkLabel,
                "undoManager.isEnabled": true,
                // enable undo & redo
            });

    function showLinkLabel(e) {
        var label = e.subject.findObject("LABEL");
        if (label !== null) label.visible = (e.subject.fromNode.data.category === "if" || e.subject.fromNode.data.category === "for");
    }

    // helper definitions for node templates
    function nodeStyle() {
        return [
            // The Node.location comes from the "loc" property of the node data,
            // converted by the Point.parse static method.
            // If the Node.location is changed, it updates the "loc" property of the node data,
            // converting back using the Point.stringify static method.
            new go.Binding("location", "loc", go.Point.parse).makeTwoWay(go.Point.stringify),
            {
                // the Node.location is at the center of each node
                locationSpot: go.Spot.Center
            }
        ];
    }

    // Define a function for creating a "port" that is normally transparent.
    // The "name" is used as the GraphObject.portId,
    // the "align" is used to determine where to position the port relative to the body of the node,
    // the "spot" is used to control how links connect with the port and whether the port
    // stretches along the side of the node,
    // and the boolean "output" and "input" arguments control whether the user can draw links from or to the port.
    function makePort(name, align, spot, output, input) {
        var horizontal = align.equals(go.Spot.Top) || align.equals(go.Spot.Bottom);
        // the port is basically just a transparent rectangle that stretches along the side of the node,
        // and becomes colored when the mouse passes over it
        return $(go.Shape,
            {
                fill: "transparent",  // changed to a color in the mouseEnter event handler
                strokeWidth: 0,  // no stroke
                width: horizontal ? NaN : 8,  // if not stretching horizontally, just 8 wide
                height: !horizontal ? NaN : 8,  // if not stretching vertically, just 8 tall
                alignment: align,  // align the port on the main Shape
                stretch: (horizontal ? go.GraphObject.Horizontal : go.GraphObject.Vertical),
                portId: name,  // declare this object to be a "port"
                fromSpot: spot,  // declare where links may connect at this port
                fromLinkable: output,  // declare whether the user may draw links from here
                toSpot: spot,  // declare where links may connect at this port
                toLinkable: input,  // declare whether the user may draw links to here
                cursor: "pointer",  // show a different cursor to indicate potential link point
                mouseEnter: function (e, port) {  // the PORT argument will be this Shape
                    if (!e.diagram.isReadOnly) port.fill = "rgba(255,0,255,0.5)";
                },
                mouseLeave: function (e, port) {
                    port.fill = "transparent";
                }
            });
    }

    function textStyle() {
        return {
            font: "bold 11pt Lato",
            stroke: "#494646"
        }
    }

    function geoFunc(geoname) {
        var geo = icons[geoname];
        if (geo === undefined) geo = icons["cogs"];  // use this for an unknown icon name
        if (typeof geo === "string") {
            geo = icons[geoname] = go.Geometry.parse(geo, true);  // fill each geometry
        }
        return geo;
    }

    // define the Node templates for regular nodes
    myDiagram.nodeTemplateMap.add("component",  // the default category
        $(go.Node, "Table", nodeStyle(),
            $(go.Panel, go.Panel.Vertical,
                $(go.Panel, "Spot",
                    $(go.Shape, "Rectangle",
                        {fill: "lightcoral", strokeWidth: 0, width: 60, height: 60},
                        new go.Binding("fill", "color")),
                    $(go.Shape,
                        {margin: 3, fill: "#F5F5F5", strokeWidth: 0},
                        new go.Binding("geometry", "geo", geoFunc))
                ),
                $(go.TextBlock, textStyle(),
                    new go.Binding("text")),
            ),


            // four named ports, one on each side:
            makePort("T", go.Spot.Top, go.Spot.Top, true, true),
            makePort("L", go.Spot.Left, go.Spot.Left, true, true),
            makePort("R", go.Spot.Right, go.Spot.Right, true, true),
            makePort("B", go.Spot.Bottom, go.Spot.Bottom, true, true)
        ));
    myDiagram.nodeTemplateMap.add("start",
        $(go.Node, "Table", nodeStyle(),
            $(go.Panel, go.Panel.Vertical,
                $(go.Panel, "Spot",
                    $(go.Shape, "Circle",
                        {fill: "lightcoral", strokeWidth: 0, width: 60, height: 60},
                        new go.Binding("fill", "color"),
                    ),
                    $(go.Shape,
                        {margin: 3, fill: "#F5F5F5", strokeWidth: 0},
                        new go.Binding("geometry", "geo", geoFunc))
                ),
                $(go.TextBlock, textStyle(),
                    new go.Binding("text")),
            ),

            makePort("T", go.Spot.Top, go.Spot.Top, true, false),
            makePort("L", go.Spot.Left, go.Spot.Left, true, false),
            makePort("R", go.Spot.Right, go.Spot.Right, true, false),
            makePort("B", go.Spot.Bottom, go.Spot.Bottom, true, false)
        ));
    myDiagram.nodeTemplateMap.add("end",
        $(go.Node, "Table", nodeStyle(),
            $(go.Panel, go.Panel.Vertical,
                $(go.Panel, "Spot",
                    $(go.Shape, "Circle",
                        {fill: "lightcoral", strokeWidth: 0, width: 60, height: 60},
                        new go.Binding("fill", "color")),
                    $(go.Shape,
                        {margin: 3, fill: "#F5F5F5", strokeWidth: 0},
                        new go.Binding("geometry", "geo", geoFunc))
                ),
                $(go.TextBlock, textStyle(),
                    new go.Binding("text")),
            ),

            makePort("T", go.Spot.Top, go.Spot.Top, false, true),
            makePort("L", go.Spot.Left, go.Spot.Left, false, true),
            makePort("R", go.Spot.Right, go.Spot.Right, false, true),
            makePort("B", go.Spot.Bottom, go.Spot.Bottom, false, true)
        ));

    myDiagram.nodeTemplateMap.add("Conditional",
        $(go.Node, "Table", nodeStyle(),
            // the main object is a Panel that surrounds a TextBlock with a rectangular Shape
            $(go.Panel, "Auto",
                $(go.Shape, "Diamond",
                    {fill: "#282c34", stroke: "#00A9C9", strokeWidth: 0},
                    new go.Binding("figure", "figure")),
                $(go.TextBlock, textStyle(),
                    {
                        margin: 8,
                        maxSize: new go.Size(160, NaN),
                        wrap: go.TextBlock.WrapFit,
                        editable: true
                    },
                    new go.Binding("text").makeTwoWay())
            ),
            // four named ports, one on each side:
            makePort("T", go.Spot.Top, go.Spot.Top, true, true),
            makePort("L", go.Spot.Left, go.Spot.Left, true, true),
            makePort("R", go.Spot.Right, go.Spot.Right, true, true),
            makePort("B", go.Spot.Bottom, go.Spot.Bottom, true, true)
        ));

    myDiagram.nodeTemplateMap.add("if",
        $(go.Node, "Table", nodeStyle(),
            $(go.Panel, go.Panel.Vertical,
                $(go.Panel, "Spot",
                    $(go.Shape, "Diamond",
                        {fill: "lightcoral", strokeWidth: 0, width: 60, height: 60},
                        new go.Binding("fill", "color")),
                    $(go.Shape,
                        {margin: 3, fill: "#F5F5F5", strokeWidth: 0},
                        new go.Binding("geometry", "geo", geoFunc))
                ),
                $(go.TextBlock, textStyle(),
                    new go.Binding("text")),
            ),

            makePort("T", go.Spot.Top, go.Spot.Top, true, true),
            makePort("L", go.Spot.Left, go.Spot.Left, true, true),
            makePort("R", go.Spot.Right, go.Spot.Right, true, true),
            makePort("B", go.Spot.Bottom, go.Spot.Bottom, true, true)
        ));

    myDiagram.nodeTemplateMap.add("for",
        $(go.Node, "Table", nodeStyle(),
            $(go.Panel, go.Panel.Vertical,
                $(go.Panel, "Spot",
                    $(go.Shape, "Circle",
                        {fill: "lightcoral", strokeWidth: 0, width: 60, height: 60},
                        new go.Binding("fill", "color")),
                    $(go.Shape,
                        {margin: 3, fill: "#F5F5F5", strokeWidth: 0},
                        new go.Binding("geometry", "geo", geoFunc))
                ),
                $(go.TextBlock, textStyle(),
                    new go.Binding("text")),
            ),

            makePort("T", go.Spot.Top, go.Spot.Top, true, true),
            makePort("L", go.Spot.Left, go.Spot.Left, true, true),
            makePort("R", go.Spot.Right, go.Spot.Right, true, true),
            makePort("B", go.Spot.Bottom, go.Spot.Bottom, true, true)
        ));

    myDiagram.nodeTemplateMap.add("break",
        $(go.Node, "Table", nodeStyle(),
            $(go.Panel, go.Panel.Vertical,
                $(go.Panel, "Spot",
                    $(go.Shape, "Circle",
                        {fill: "lightcoral", strokeWidth: 0, width: 60, height: 60},
                        new go.Binding("fill", "color")),
                    $(go.Shape,
                        {margin: 3, fill: "#F5F5F5", strokeWidth: 0},
                        new go.Binding("geometry", "geo", geoFunc))
                ),
                $(go.TextBlock, textStyle(),
                    new go.Binding("text")),
            ),

            makePort("T", go.Spot.Top, go.Spot.Top, true, true),
            makePort("L", go.Spot.Left, go.Spot.Left, true, true),
            makePort("R", go.Spot.Right, go.Spot.Right, true, true),
            makePort("B", go.Spot.Bottom, go.Spot.Bottom, true, true)
        ));


    myDiagram.linkTemplate =
        $(go.Link,  // the whole link panel
            {
                routing: go.Link.AvoidsNodes,
                curve: go.Link.JumpOver,
                corner: 5, toShortLength: 4,
                relinkableFrom: true,
                relinkableTo: true,
                reshapable: true,
                resegmentable: true,
                // mouse-overs subtly highlight links:
                mouseEnter: function (e, link) {
                    link.findObject("HIGHLIGHT").stroke = "rgba(30,144,255,0.2)";
                },
                mouseLeave: function (e, link) {
                    link.findObject("HIGHLIGHT").stroke = "transparent";
                },
                selectionAdorned: false
            },
            new go.Binding("points").makeTwoWay(),
            $(go.Shape,  // the highlight shape, normally transparent
                {isPanelMain: true, strokeWidth: 8, stroke: "transparent", name: "HIGHLIGHT"}),
            $(go.Shape,  // the link path shape
                {isPanelMain: true, stroke: "gray", strokeWidth: 2},
                new go.Binding("stroke", "isSelected", function (sel) {
                    return sel ? "dodgerblue" : "gray";
                }).ofObject()),
            $(go.Shape,  // the arrowhead
                {toArrow: "standard", strokeWidth: 0, fill: "gray"}),
            $(go.Panel, "Auto",  // the link label, normally not visible
                {visible: false, name: "LABEL", segmentIndex: 2, segmentFraction: 0.5},
                new go.Binding("visible", "visible").makeTwoWay(),
                $(go.Shape, "RoundedRectangle",  // the label shape
                    {fill: "#F8F8F8", strokeWidth: 0}),
                $(go.TextBlock, "",  // the label
                    {
                        textAlign: "center",
                        font: "10pt helvetica, arial, sans-serif",
                        stroke: "#333333",
                        editable: false
                    },
                    new go.Binding("text").makeTwoWay())
            ),
        );
    myDiagram.toolManager.linkingTool.temporaryLink.routing = go.Link.Orthogonal;
    myDiagram.toolManager.relinkingTool.temporaryLink.routing = go.Link.Orthogonal;
    myDiagram.model = go.Model.fromJson(document.getElementById("mySavedModel").value);  // load an initial diagram from some JSON text

    jQuery("#accordion").accordion({
        classes: {
            "ui-accordion-header": "color1",
            "ui-accordion-header-active": "color2"
        },
        activate: function (event, ui) {
            myPaletteSmall.requestUpdate();
            myPaletteTall.requestUpdate();
            myPaletteWide.requestUpdate();
            myPaletteBig.requestUpdate();
        }
    });

    // initialize the first Palette
    myPaletteSmall =
        $(go.Palette, "myPaletteSmall",
            { // share the templates with the main Diagram
                nodeTemplateMap: myDiagram.nodeTemplateMap,
            });


    // specify the contents of the Palette
    myPaletteSmall.model = new go.GraphLinksModel([
        {category: "start", text: "开始", geo: "start", color: colors["blue"]},
        {category: "end", text: "结束", geo: "end", color: colors["blue"]},
        {category: "if", text: "判断", geo: "if", color: colors["blue"]},
        {category: "for", text: "循环", geo: "for", color: colors["blue"]},
        {category: "break", text: "跳出", geo: "break", color: colors["blue"]},

    ]);

    // initialize the second Palette, of tall items
    myPaletteTall =
        $(go.Palette, "myPaletteTall",
            { // share the templates with the main Diagram
                nodeTemplateMap: myDiagram.nodeTemplateMap,
            });

    // specify the contents of the Palette
    myPaletteTall.model = new go.GraphLinksModel([
        {category: "component", text: "加1", guid: "swerswersrsdf", geo: "cogs", color: colors["blue"]},
        {category: "component", text: "控件2", guid: "swerswersrsdfsas", geo: "cogs", color: colors["blue"]},
    ]);

    // initialize the third Palette, of wide items
    myPaletteWide =
        $(go.Palette, "myPaletteWide",
            { // share the templates with the main Diagram
                nodeTemplateMap: myDiagram.nodeTemplateMap,
            });

    // specify the contents of the Palette
    myPaletteWide.model = new go.GraphLinksModel([
        {category: "End", text: "End"}
    ]);

    // initialize the fourth Palette, of big items
    myPaletteBig =
        $(go.Palette, "myPaletteBig",
            { // share the templates with the main Diagram
                nodeTemplateMap: myDiagram.nodeTemplateMap,
            });

    // specify the contents of the Palette
    myPaletteBig.model = new go.GraphLinksModel([
        {category: "End", text: "End"},
    ]);

    //DataInspector
    myDiagram.model.modelData = {
        id: 1,
        guid: "68d3b594-44d0-11eb-800a-84fdd1a17907",
        pnode: "无",
        createtime: "2021-01-01 00:00:00",
        createuser: "系统管理员",
        updatetime: "2021-01-21 00:00:00",
        updateuser: "系统管理员",
        longname: "测试流程",
        shortname: "测试流程",
        owner: "USER",
        icon: "",
        version: "1.0",
        remark: "测试",
        group: [1],
        input: [{code: "startnum", name: "开始数字", type: "int", source: "input", value: "", remark: "", sort: "2"}],
        variable: [{code: "num", name: "数字", type: "int", value: "", remark: "", sort: "1"}],
        output:[{code: "number", name: "结束数字", type: "int", source: "workfolwVariable", value: "number", remark: "", sort: "1"}]
    };
    myDiagram.select(myDiagram.nodes.first());
    var inspector = new Inspector(myDiagram);

});

$(document).ready(function () {
    //流程输入
    if ($('#workflow_input_source').val() == "function") {
        $('#workflow_input_value_lable').text("公式");
    } else if ($('#workflow_input_source').val() == "input") {
        $('#workflow_input_value_lable').text("默认值");
    } else {
        $('#workflow_input_value_lable').text("值");
    }

    $('#workflow_input_source').change(function () {
        if ($('#workflow_input_source').val() == "function") {
            $('#workflow_input_value_lable').text("公式");
        } else if ($('#workflow_input_source').val() == "input") {
            $('#workflow_input_value_lable').text("默认值");
        } else {
            $('#workflow_input_value_lable').text("值");
        }
    })

    //流程输出
    if ($('#workflow_output_source').val() == "function") {
        $('#workflow_output_value_lable').text("公式");
    } else if ($('#workflow_output_source').val() == "output") {
        $('#workflow_output_value_lable').text("默认值");
    } else if ($('#workflow_output_source').val() == "workfolwInput") {
        $('#workflow_output_value_lable').text("参数名");
    } else if ($('#workflow_output_source').val() == "workfolwVariable") {
        $('#workflow_output_value_lable').text("变量名");
    } else if ($('#workflow_output_source').val() == "stepOutput") {
        $('#workflow_output_value_lable').text("步骤及参数");
    }else {
        $('#workflow_output_value_lable').text("值");
    }

    $('#workflow_output_source').change(function () {
        if ($('#workflow_output_source').val() == "function") {
            $('#workflow_output_value_lable').text("公式");
        } else if ($('#workflow_output_source').val() == "output") {
            $('#workflow_output_value_lable').text("默认值");
        } else if ($('#workflow_output_source').val() == "workfolwInput") {
            $('#workflow_output_value_lable').text("参数名");
        } else if ($('#workflow_output_source').val() == "workfolwVariable") {
            $('#workflow_output_value_lable').text("变量名");
        } else if ($('#workflow_output_source').val() == "stepOutput") {
            $('#workflow_output_value_lable').text("步骤及参数");
        }else {
            $('#workflow_output_value_lable').text("值");
        }
    })


    $('#save').click(function () {
        document.getElementById("mySavedModel").value = myDiagram.model.toJson();
        myDiagram.isModified = false;
    });

});