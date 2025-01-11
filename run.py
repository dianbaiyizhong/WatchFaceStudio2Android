import os
import shutil
import zipfile
from lxml import etree

# 输入你wfs工具输出的aab文件路径
wfs_build_file_path = f"/Users/huanghaoming/Documents/GitHub/nba-watch-face/build/rod_timberwolves/com.watchfacestudio.Test_51844260478405176971266896599403_debug.aab"
# 给你的工程起个英文名
project_name = "watchface_timberwolves"
# 起app名字
app_name = "明尼苏达森林狼"
# appid
appId = "com.nntk.watch.nba.timberwolves"

# 把你图片目录配置进来
drawable_dir = [
    '/Users/huanghaoming/Documents/GitHub/nba-watch-face/watch-face-studio-project/timberwolves_res/upscayl_png_realesrgan-x4plus-anime_2x',
    '/Users/huanghaoming/Documents/GitHub/nba-watch-face/watch-face-studio-project/movie_timberwolves']

drawable_files = [
    '/Users/huanghaoming/Documents/GitHub/nba-watch-face/watch-face-studio-project/empty.png'
]

# 把你字体文件路径配置进来
font_files = ['/Users/huanghaoming/Documents/GitHub/nba-watch-face/watch-face-studio-project/font_timberwolves.TTF']

# 无非是为了能修改图片动画的速率，将要调整的速率设置在这里
frame_rates = ["45", "60"]


def prettify_xml_string_lxml(xml_string):
    # 解析 XML 字符串
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_string, parser)

    # 将 ElementTree 转换为漂亮的字符串表示
    pretty_xml = etree.tostring(root, pretty_print=True, encoding='unicode')

    return pretty_xml


def replace_template(key, value):
    for root, dirs, files in os.walk(project_name):
        for file in files:
            # 判断文件是否是xml，kts文件
            if not file.endswith(('.xml', '.kts')):
                continue
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                content = f.read()
                new_content = content.replace('${' + key + '}', value)
                with open(file_path, 'w') as f1:
                    f1.write(new_content)


if __name__ == '__main__':
    # 复制android-studio-template为project_name，如果存在就删除再复制
    if os.path.exists(project_name):
        shutil.rmtree(project_name)
    shutil.copytree('android-studio-template', project_name)
    # 获取aab文件所在目录和文件名
    aab_dir = os.path.dirname(wfs_build_file_path)
    aab_name = os.path.basename(wfs_build_file_path)

    # 构造zip文件路径
    zip_path = os.path.join(aab_dir, aab_name.replace('.aab', '.zip'))

    # 复制aab文件为zip文件
    shutil.copy2(wfs_build_file_path, zip_path)

    # 解压zip文件

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # 创建解压目录，如果存在则删除
        extract_dir = os.path.join(aab_dir, 'extracted')
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        else:
            os.makedirs(extract_dir)

        # 解压文件
        zip_ref.extractall(extract_dir)

        print('文件已解压到:', extract_dir)
    watch_face_xml_dir = os.path.join(extract_dir, 'base', 'res', 'raw', 'watchface.xml')
    # 格式化xml文件，使内容好看一点，调用prettify_xml_string_lxml
    with open(watch_face_xml_dir, 'r') as f:
        xml_string = f.read()
        pretty_xml = prettify_xml_string_lxml(xml_string)
        with open(watch_face_xml_dir, 'w') as f1:
            f1.write(pretty_xml)
    # 将解压出来的watchface.xml文件复制到工程的project_name/app/src/main/res/raw目录下
    shutil.copy2(watch_face_xml_dir, os.path.join(project_name, 'app', 'src', 'main', 'res', 'raw'))

    # drawable-nodpi-v4文件夹的preview.png图片复制到工程的project_name/app/src/main/res/drawable
    preview_png_dir = os.path.join(extract_dir, 'base', 'res', 'drawable-nodpi-v4', 'preview.png')
    shutil.copy2(preview_png_dir, os.path.join(project_name, 'app', 'src', 'main', 'res', 'drawable'))

    # 替换project_name目录下的所有文件中出现${}的字符串，用模板来替换
    replace_template('projectName', project_name)
    replace_template('appName', app_name)
    replace_template('appId', appId)

    # 将drawable_dir路径集合中的所有文件复制到project_name/app/src/main/res/drawable目录下，只需要遍历一层目录即可
    for dir in drawable_dir:
        for root, dirs, files in os.walk(dir):
            for file in files:
                shutil.copy2(os.path.join(root, file),
                             os.path.join(project_name, 'app', 'src', 'main', 'res', 'drawable'))
    # 将font_dir所有文件复制到project_name/app/src/main/res/font目录下
    for dir in font_files:
        shutil.copy2(dir, os.path.join(project_name, 'app', 'src', 'main', 'res', 'font'))

    # 将drawable_files所有文件复制到project_name/app/src/main/res/drawable目录下
    for dir in drawable_files:
        shutil.copy2(dir, os.path.join(project_name, 'app', 'src', 'main', 'res', 'drawable'))

    # 找watch_face_xml_dir这个xml中有多少个<SequenceImages>标签,将他子元素<Image>的resource属性全部重命名为根据_分割去掉首个和最后一个，保留中间的字符串
    wfx_dest = os.path.join(project_name, 'app', 'src', 'main', 'res', 'raw', 'watchface.xml')
    with open(wfx_dest, 'r') as f:
        xml_string = f.read()
        root = etree.fromstring(xml_string)
        for index, sequence_images in enumerate(root.findall('.//SequenceImages'), start=0):
            sequence_images.attrib['frameRate'] = frame_rates[index]
            for image in sequence_images.findall('.//Image'):
                resource = image.get('resource')
                new_resource = '_'.join(resource.split('_')[1:-5])
                image.set('resource', new_resource)
        pretty_xml = prettify_xml_string_lxml(etree.tostring(root, encoding='unicode'))
        with open(wfx_dest, 'w') as f1:
            f1.write(pretty_xml)

    # 替换字体
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(wfx_dest, parser)
    root = tree.getroot()
    # 查找所有的 <Font> 元素，并设置它们的 family 属性
    for font in root.xpath('.//Font'):
        resource = font.get('family')
        new_resource = '_'.join(resource.split('_')[1:-5])
        font.set('family', new_resource)
    # 将修改后的 XML 写回文件
    tree.write(wfx_dest, pretty_print=True,
               xml_declaration=True, encoding='utf-8')

    # 替换Thumbnail
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(wfx_dest, parser)
    root = tree.getroot()
    # 查找所有的 <Font> 元素，并设置它们的 family 属性
    for font in root.xpath('.//Thumbnail'):
        resource = font.get('resource')
        new_resource = '_'.join(resource.split('_')[1:-5])
        font.set('resource', new_resource)
    # 将修改后的 XML 写回文件
    tree.write(wfx_dest, pretty_print=True,
               xml_declaration=True, encoding='utf-8')
