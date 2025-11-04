#!/usr/bin/env python3
"""
스크립트: en/와 ko/ 디렉토리의 마크다운 파일을 읽어서 YAML 파일로 변환합니다.
날짜 순으로 정렬되며, 최신 날짜가 위에 옵니다.
"""

import os
import re
from pathlib import Path
from datetime import datetime
import yaml


# YAML에서 multiline 문자열을 literal block scalar(|)로 저장하기 위한 설정
class LiteralStr(str):
    pass


def literal_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


yaml.add_representer(LiteralStr, literal_str_representer)


def extract_date_from_filename(filename):
    """파일명에서 날짜를 추출합니다. (예: 2025-11-04.md -> 2025-11-04)"""
    match = re.match(r'(\d{4}-\d{2}-\d{2})\.md$', filename)
    if match:
        return match.group(1)
    return None


def read_markdown_files(directory):
    """디렉토리에서 모든 마크다운 파일을 읽어서 리스트로 반환합니다."""
    files_data = []
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"경고: 디렉토리 {directory}가 존재하지 않습니다.")
        return files_data
    
    # 언어 추출 (디렉토리명에서)
    language = dir_path.name
    
    # .md 파일 찾기
    for md_file in dir_path.glob('*.md'):
        date_str = extract_date_from_filename(md_file.name)
        if date_str:
            try:
                # 파일 내용 읽기
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read().rstrip()  # 끝의 공백 제거
                
                files_data.append({
                    'date': date_str,
                    'language': language,
                    'content': LiteralStr(content)
                })
            except Exception as e:
                print(f"경고: 파일 {md_file} 읽기 실패: {e}")
        else:
            print(f"경고: 파일명에서 날짜를 추출할 수 없습니다: {md_file.name}")
    
    return files_data


def generate_yaml():
    """en/와 ko/ 디렉토리의 파일들을 읽어서 YAML 파일을 생성합니다."""
    base_dir = Path(__file__).parent
    
    # 모든 파일 데이터 수집
    all_files = []
    
    # en/ 디렉토리 읽기
    all_files.extend(read_markdown_files(base_dir / 'en'))
    
    # ko/ 디렉토리 읽기
    all_files.extend(read_markdown_files(base_dir / 'ko'))
    
    if not all_files:
        print("경고: 처리할 파일이 없습니다.")
        return
    
    # 날짜순으로 정렬 (최신이 위로)
    def sort_key(item):
        try:
            return datetime.strptime(item['date'], '%Y-%m-%d')
        except:
            return datetime.min
    
    all_files.sort(key=sort_key, reverse=True)
    
    # YAML 형식으로 변환 (이미 LiteralStr로 변환되어 있음)
    yaml_data = all_files
    
    # YAML 파일로 저장
    output_file = base_dir / 'notifications.yaml'
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, 
                  sort_keys=False, width=1000)
    
    print(f"✅ YAML 파일이 생성되었습니다: {output_file}")
    print(f"   총 {len(yaml_data)}개의 항목이 포함되었습니다.")


if __name__ == '__main__':
    generate_yaml()

