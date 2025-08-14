# **iptvTool**

一个用于抓取 IPTV 原始数据、生成 iptv.json 和 M3U 播放列表的命令行工具。支持单播（unicast）、组播（multicast）播放列表生成，并可按自定义排序文件输出。

## **功能**

- 📡 **抓取 IPTV 原始数据**
- 🛠 **生成 iptv.json 数据文件**
- 🎯 **生成单播 M3U 播放列表**
- 🌐 **生成组播 M3U 播放列表**
- 🔄 **支持全流程执行（fetch + process + m3u all）**
- 🗂 **支持自定义排序文件和输出目录**

## **使用方法**

### **基本命令结构**

```
python main.py [OPTIONS]
```

### **可用参数**

| **参数**            | **说明**                               |
| ------------------- | -------------------------------------- |
| --fetch             | 抓取 IPTV 原始数据                     |
| --process           | 生成 iptv.json                         |
| `–m3u [uni          | mul                                    |
| --sort-file <路径>  | 排序文件路径，默认 sort.txt            |
| --output-dir <路径> | 输出目录，默认 playlist                |
| --input-json <路径> | IPTV JSON 数据文件路径，默认 iptv.json |
| --all               | 执行 fetch + process + m3u all 全流程  |

### **示例**

**抓取原始数据**

```
python main.py --fetch
```

**生成 iptv.json**

```
python main.py --process
```

**生成单播播放列表**

```
python main.py --m3u uni
```

**生成组播播放列表**

```
python main.py --m3u mul
```

**全流程执行（抓取 + 生成 JSON + 生成全部播放列表）**

```
python main.py --all
```

**使用自定义排序文件和输出目录**

```
python main.py --all --sort-file mysort.txt --output-dir myplaylist
```

## **输出文件**

默认情况下，输出目录为 playlist/：

- unicast.m3u → 单播播放列表
- multicast.m3u → 组播播放列表
- iptv.json → IPTV 数据文件

