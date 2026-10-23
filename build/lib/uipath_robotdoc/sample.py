"""Builds a small, realistic .nupkg so the tool can be tried (and tested) without a real robot."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

NS = ('xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities" '
      'xmlns:ui="http://schemas.uipath.com/workflow/activities" '
      'xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" '
      'xmlns:sap2010="http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation" '
      'xmlns:scg="clr-namespace:System.Collections.Generic;assembly=mscorlib"')

MAIN = f"""<Activity x:Class="Main" {NS}>
  <x:Members>
    <x:Property Name="in_Config" Type="InArgument(scg:Dictionary(x:String, x:Object))" />
    <x:Property Name="out_Status" Type="OutArgument(x:String)" />
  </x:Members>
  <Sequence DisplayName="Main Sequence" sap2010:Annotation.AnnotationText="Entry point: init, process queue items, close.">
    <Sequence.Variables>
      <Variable x:TypeArguments="x:Int32" Name="retryCount" Default="3" />
      <Variable x:TypeArguments="x:String" Name="status" />
    </Sequence.Variables>
    <ui:LogMessage DisplayName="Log start" Level="Info" Message="[&quot;Process started&quot;]" />
    <ui:InvokeWorkflowFile DisplayName="Initialize" WorkflowFileName="Framework\\Init.xaml" />
    <ui:InvokeWorkflowFile DisplayName="Process item" WorkflowFileName="Process.xaml">
      <ui:InvokeWorkflowFile.Arguments>
        <InArgument x:TypeArguments="x:String" x:Key="in_Item">[status]</InArgument>
      </ui:InvokeWorkflowFile.Arguments>
    </ui:InvokeWorkflowFile>
    <TryCatch DisplayName="Close apps safely">
      <TryCatch.Try><ui:InvokeWorkflowFile DisplayName="Close" WorkflowFileName="Missing.xaml" /></TryCatch.Try>
    </TryCatch>
  </Sequence>
</Activity>"""

INIT = f"""<Activity x:Class="Init" {NS}>
  <Sequence DisplayName="Init">
    <ui:ReadRange DisplayName="Read Config" FilePath="Data\\Config.xlsx" />
    <Assign DisplayName="Set status" />
  </Sequence>
</Activity>"""

PROCESS = f"""<Activity x:Class="Process" {NS}>
  <x:Members><x:Property Name="in_Item" Type="InArgument(x:String)" /></x:Members>
  <Sequence DisplayName="Process Item">
    <ui:OpenBrowser DisplayName="Open portal" Url="https://example.com/portal" />
    <ui:TypeInto DisplayName="Type name" Selector="&lt;html app='chrome.exe' /&gt;&lt;webctrl id='name' /&gt;" />
    <If DisplayName="Is valid?">
      <If.Then><ui:Click DisplayName="Submit" Selector="&lt;webctrl id='submit' /&gt;" /></If.Then>
      <If.Else><ui:LogMessage DisplayName="Log invalid" Level="Warn" Message="[&quot;Invalid&quot;]" /></If.Else>
    </If>
  </Sequence>
</Activity>"""

ORPHAN = f"""<Activity x:Class="Unused" {NS}><Sequence DisplayName="Unused"><Delay DisplayName="Wait" /></Sequence></Activity>"""


def write_sample_nupkg(path: Path) -> Path:
    project = {
        "name": "InvoiceBot", "description": "Sample REFramework-style robot.", "main": "Main.xaml",
        "dependencies": {"UiPath.System.Activities": "[23.10.4]", "UiPath.UIAutomation.Activities": "[23.10.7]"},
        "projectVersion": "1.0.3", "expressionLanguage": "VisualBasic", "targetFramework": "Windows",
    }
    nuspec = ('<?xml version="1.0"?><package xmlns="http://schemas.microsoft.com/packaging/2012/06/nuspec.xsd">'
              "<metadata><id>InvoiceBot</id><version>1.0.3</version><authors>RPA Team</authors>"
              "<description>Sample REFramework-style robot.</description></metadata></package>")
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("InvoiceBot.nuspec", nuspec)
        zf.writestr("content/project.json", json.dumps(project, indent=2))
        zf.writestr("content/Main.xaml", MAIN)
        zf.writestr("content/Process.xaml", PROCESS)
        zf.writestr("content/Framework/Init.xaml", INIT)
        zf.writestr("content/Framework/Unused.xaml", ORPHAN)
    return path
