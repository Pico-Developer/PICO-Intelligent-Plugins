using System;
using System.Linq;

using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class VibeLabExport
{
    public static void Run()
    {
        try
        {
            string output = Environment.GetEnvironmentVariable("VIBELAB_EXPORT_DIR");
            if (string.IsNullOrWhiteSpace(output))
            {
                throw new InvalidOperationException("VIBELAB_EXPORT_DIR is not set.");
            }

            string[] scenes = EditorBuildSettings.scenes
                .Where(scene => scene.enabled)
                .Select(scene => scene.path)
                .ToArray();
            if (scenes.Length == 0)
            {
                throw new InvalidOperationException("No enabled scenes are configured.");
            }

            if (PlayerSettings.GetScriptingBackend(NamedBuildTarget.Android) !=
                ScriptingImplementation.IL2CPP)
            {
                throw new InvalidOperationException("Android scripting backend must be IL2CPP.");
            }

            AndroidArchitecture architectures = PlayerSettings.Android.targetArchitectures;
            if (architectures != AndroidArchitecture.ARM64)
            {
                throw new InvalidOperationException(
                    "Android target architectures must contain ARM64 only.");
            }

            if (PlayerSettings.Android.useCustomKeystore)
            {
                throw new InvalidOperationException(
                    "Custom Android keystore must be disabled for the export.");
            }

            EditorUserBuildSettings.exportAsGoogleAndroidProject = true;
            EditorUserBuildSettings.buildAppBundle = false;
            EditorUserBuildSettings.androidBuildSystem = AndroidBuildSystem.Gradle;

            BuildReport report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = output,
                target = BuildTarget.Android,
                options = BuildOptions.None
            });

            Debug.Log(
                "VibeLab export result=" + report.summary.result
                + " errors=" + report.summary.totalErrors
                + " warnings=" + report.summary.totalWarnings
                + " output=" + output);

            EditorApplication.Exit(
                report.summary.result == BuildResult.Succeeded ? 0 : 1);
        }
        catch (Exception exception)
        {
            Debug.LogException(exception);
            EditorApplication.Exit(1);
        }
    }
}
