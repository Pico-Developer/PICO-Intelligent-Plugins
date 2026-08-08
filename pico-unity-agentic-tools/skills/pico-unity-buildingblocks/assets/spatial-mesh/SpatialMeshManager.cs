#if ENABLE_PICO_XR_SDK
/*******************************************************************************
Copyright © 2015-2022 PICO Technology Co., Ltd.All rights reserved.  

NOTICE：All information contained herein is, and remains the property of 
PICO Technology Co., Ltd. The intellectual and technical concepts 
contained herein are proprietary to PICO Technology Co., Ltd. and may be 
covered by patents, patents in process, and are protected by trade secret or 
copyright law. Dissemination of this information or reproduction of this 
material is strictly forbidden unless prior written permission is obtained from
PICO Technology Co., Ltd. 
*******************************************************************************/
using System;
using System.Collections.Generic;
using System.Linq;
using ByteDance.PICO.XR;
using UnityEngine;
using UnityEngine.XR;
using UnityEngine.XR.Management;

public class SpatialMeshManager : MonoBehaviour
{
    public static SpatialMeshManager Instance { get; private set; }
    // todo: for debugging
    [Header("General configuration")]
    [SerializeField] private int maxRenderPerFrame = 100; // max render count per frame
    [SerializeField] private int meshAmount = 200;
    [Header("Material and container")]
    [SerializeField] private Transform meshContainer; // mesh container
    [SerializeField] private GameObject meshPrefab; // prefab
    [SerializeField] private Material wireframeMaterial;
    // todo: replace with the final stencil-based transparent material
    [SerializeField] private Material transparentMaterial;
    private readonly Dictionary<Guid, GameObject> spaticalMeshList = new();
    private readonly Dictionary<Guid, PxrSpatialMeshInfo> needUpdateMeshList = new();
    private readonly Queue<GameObject> pool = new();
    private XRMeshSubsystem system;
    private Mesh mesh;
    private Transform _camera;
    private readonly object listLock = new();
    private bool isStopUpdateMesh = false;
    // todo: for debugging
    void Awake()
    {
       if (Instance != null)
        {
            Destroy(gameObject);
            Debug.LogError($"Multiple instances of this singleton exist!");
        }
        else
        {
            Destroy(Instance);
            Instance = this;
        }
    }
    void Start()
    {
        _camera = Camera.main.transform;
        InitSystem();

    }
    public void StopUpdate()
    {
        StopUpdateMesh();
    }
    private void InitSystem()
    {
        if (XRGeneralSettings.Instance != null && XRGeneralSettings.Instance.Manager != null)
        {
            var pxrLoader = XRGeneralSettings.Instance.Manager.ActiveLoaderAs<PXR_Loader>();
            if (pxrLoader != null)
            {
                system = pxrLoader.meshSubsystem;
                if (system != null)
                {
                    system.Start();
                    if (system.running) PXR_Manager.SpatialMeshDataUpdated += PXR_OnSpatialMeshDataUpdated;
                }
                else
                {
                    Debug.LogWarning("The meshSubsystem cannot be obtained in this runtime environment");
                }
            }
        }
        for (var i = 0; i < meshAmount; i++)
        {
            var mesh = Instantiate(meshPrefab, meshContainer);
            pool.Enqueue(mesh);
            mesh.SetActive(false);
        }
    }
    void Update()
    {
        if(isStopUpdateMesh) return;
        Shader.SetGlobalVector("_TargetPosition", _camera.position);
        if (needUpdateMeshList.Count > 0)
        {
            lock (listLock)
            {
                var keysToRemove = needUpdateMeshList.Keys.Take(maxRenderPerFrame).ToList();
                foreach (var key in keysToRemove)
                {
                    MeshUpdateQueue(needUpdateMeshList[key]);
                }
                // remove the records corresponding to these keys
                foreach (var key in keysToRemove)
                {
                    needUpdateMeshList.Remove(key);
                }
            }
        }
    }

    private void MeshUpdateQueue(PxrSpatialMeshInfo pxrSpatialMeshInfo)
    {
        var id = pxrSpatialMeshInfo.uuid;
        switch (pxrSpatialMeshInfo.state)
        {
            case MeshChangeState.Added:
            case MeshChangeState.Updated:
                if (spaticalMeshList.ContainsKey(id))
                {
                    CreateMesh(pxrSpatialMeshInfo, spaticalMeshList[id]);
                }
                else
                {
                    GameObject newMesh = GetMeshFromPool();
                    spaticalMeshList.Add(id, newMesh);
                    CreateMesh(pxrSpatialMeshInfo, newMesh);
                }
                break;
            case MeshChangeState.Removed:
                if (spaticalMeshList.ContainsKey(id))
                {
                    SetMeshFromPool(spaticalMeshList[id]);
                    spaticalMeshList.Remove(id);
                }
                break;
            default:
                break;
        }
    }

    private GameObject GetMeshFromPool()
    {
        GameObject mesh;
        if (pool.Count > 0)
        {
            mesh = pool.Dequeue();
            mesh.SetActive(true);
        }
        else
        {
            mesh = Instantiate(meshPrefab, meshContainer);
            pool.Enqueue(mesh);
        }
        var renderer = mesh.GetComponent<MeshRenderer>();
        MaterialPropertyBlock props = new();
        props.SetFloat("_StartTime", Time.time);
        renderer.SetPropertyBlock(props);
        return mesh;
    }
    private void SetMeshFromPool(GameObject mesh)
    {
        mesh.SetActive(false);
        if (pool.Count > meshAmount)
        {
            Destroy(mesh);
        }
        else
        {
            pool.Enqueue(mesh);
        }
    }
    private void PXR_OnSpatialMeshDataUpdated(List<PxrSpatialMeshInfo> list)
    {
        lock (listLock)
        {
            foreach (var item in list)
            {
                if (needUpdateMeshList.ContainsKey(item.uuid))
                {
                    switch (item.state)
                    {
                        case MeshChangeState.Added:
                        case MeshChangeState.Updated:
                            needUpdateMeshList[item.uuid] = item;
                            break;
                        case MeshChangeState.Removed:
                            needUpdateMeshList.Remove(item.uuid);
                            break;
                        default:
                            break;
                    }
                }
                else
                {
                    needUpdateMeshList.Add(item.uuid, item);
                }
            }
        }
    }
    private void CreateMesh(PxrSpatialMeshInfo block, GameObject meshGameObject)
    {
        var meshFilter = meshGameObject.GetComponentInChildren<MeshFilter>();
        var meshCollider = meshGameObject.GetComponentInChildren<MeshCollider>();
        if (meshFilter.mesh == null)
        {
            mesh = new Mesh();
            mesh.Clear();
            mesh.MarkDynamic();
        }
        else
        {
            mesh = meshFilter.mesh;
            mesh.Clear();
        }
        var vertices = new List<Vector3>();
        for (var i = 0; i < block.vertices.Length; i++)
        {
            vertices.Add(block.rotation * block.vertices[i] + block.position);
        }
        mesh.SetVertices(vertices);
        mesh.SetTriangles(block.indices, 0);
        mesh.RecalculateNormals();
        meshFilter.mesh = mesh;
        if (meshCollider != null)
        {
            meshCollider.sharedMesh = mesh;
        }
    }
    private void StopUpdateMesh()
    {
        isStopUpdateMesh = true;
#if !UNITY_EDITOR
        if (system.running) PXR_Manager.SpatialMeshDataUpdated -= PXR_OnSpatialMeshDataUpdated;
#endif
    }
}
#endif
