# **Helping Hand for Blender**

A powerful Blender addon designed to rapidly select, instance, organize, and rename large numbers of objects in complex scenes. This tool is optimized for performance, using an advanced caching system to provide near-instantaneous selections even with thousands of objects.

## **The Problem**

Manually selecting, linking (instancing), sorting, and renaming thousands of duplicated objects is slow, repetitive, and tedious. This addon automates these processes with optimized, one-click solutions, saving you valuable time on large-scale projects.

## **Key Features**

* **🚀 High-Performance Caching:** The first selection builds a map of your scene. All subsequent selections are nearly instantaneous.  
* **🔎 Flexible Selection Methods:**  
  * **By Name:** Intelligently finds objects with the same base name (e.g., selecting Cube will also find Cube.001, Cube\_copy, etc.). Includes a case-sensitive option for precise control.  
  * **By Topology:** A highly accurate method that finds objects with the exact same number of vertices, edges, and faces.  
* **✅ Safe, Step-by-Step Workflow:** A clear UI to **Select**, **Link**, and **Move** objects, with each action being a separate button to prevent mistakes.  
* **🗂️ Effortless Organization:** Quickly move massive selections into a designated collection in one click.  
* **✨ NEW\! Batch Renaming:**  
  * Rename hundreds of selected objects in one click.  
  * Define a custom Prefix (e.g., SM\_), Base Name (e.g., Fern), Start Number, and Padding.  
  * Automatically renames selected objects to SM\_Fern\_01, SM\_Fern\_02, SM\_Fern\_03, etc.

## **Installation**

1. Go to the [**Releases page**](https://www.google.com/search?q=https://github.com/YOUR_USERNAME/blender-instancing-helper/releases) of this repository. (Or use the .py file directly).  
2. Download the latest helping\_hand\_vX.X.zip file (or helping\_hand.py).  
3. In Blender, go to Edit \> Preferences \> Add-ons.  
4. Click Install... and select the .zip or .py file you just downloaded.  
5. Enable the addon by checking the box next to "**Helping Hand**".

## **How to Use**

1. In the 3D Viewport, press the **N** key to open the sidebar.  
2. Find and click on the **"Helping Hand"** tab.

### **Instancing Tools**

1. **Step 1:** Choose your target collection from the dropdown menu.  
2. **Step 2:** Select a single object in your scene that you want to find duplicates of. Choose your selection method (Name or Topology) and click **"Select"**.  
3. **Step 3:** The addon will highlight all similar objects. To confirm, click **"Link Selected Data"** to instance them, and then **"Move to Collection"** to organize them.

### **Batch Renaming Tools**

1. **Step 1:** Select all the objects you want to rename in the 3D Viewport.  
2. **Step 2:** In the "Batch Renaming Tools" panel, set your desired format:  
   * **Prefix:** e.g., SM\_  
   * **Base Name:** e.g., Fern  
   * **Start:** The first number in the sequence (e.g., 1).  
   * **Padding:** The number of digits (e.g., 2 for 01, 3 for 001).  
3. **Step 3:** Check the "Example" text to see what the new name will look like.  
4. **Step 4:** Click the **"Batch Rename Selected"** button.

## **Author & License**

* **Author:** [HITANSH3D](https://www.artstation.com/hitansh3dartist)  
* **License:** This project is licensed under the MIT License.