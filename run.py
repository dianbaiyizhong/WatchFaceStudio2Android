import os
import shutil
import zipfile
from lxml import etree
import json5  # 需要先安装json5包: pip install json5

# 在文件开头添加配置文件的读取
with open('config_celtics.json5', 'r', encoding='utf-8') as f:
    config = json5.load(f)

# 从配置文件中获取变量
project_name = config.get('project_name')
app_name = config.get('app_name')
appId = config.get('appId')
wfs_build_file_path = config.get('wfs_build_file_path')
drawable_dir = config.get('drawable_dir', [])
font_files = config.get('font_files', [])
drawable_files = config.get('drawable_files', [])
frame_rates = config.get('frame_rates', [])
output_dir = config.get('outputDir')


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

    # 将project_name复制到指定目录下,如果存在，则删除
    if os.path.exists(os.path.join(output_dir, project_name)):
        shutil.rmtree(os.path.join(output_dir, project_name))
    shutil.move(project_name, os.path.join(output_dir, project_name))
