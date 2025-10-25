#!/usr/bin/env python3
"""Build Factory Droid templates for release"""

import os
import zipfile
from pathlib import Path
import shutil
import tempfile

def create_droid_template(script_type='sh', version='v0.0.21'):
    """Create Factory Droid template zip file"""
    
    print(f"Building Factory Droid template ({script_type})...")
    
    # Create temporary directory for building
    with tempfile.TemporaryDirectory() as tmpdir:
        build_dir = Path(tmpdir) / f"sdd-droid-package-{script_type}"
        build_dir.mkdir(parents=True)
        
        # Create .specify directory structure
        specify_dir = build_dir / ".specify"
        specify_dir.mkdir()
        
        # Copy base directories
        for dir_name in ['memory', 'templates']:
            src = Path(dir_name)
            if src.exists():
                dst = specify_dir / dir_name
                shutil.copytree(src, dst)
                print(f"  ✓ Copied {dir_name}")
        
        # Copy appropriate script directory
        scripts_dir = specify_dir / "scripts"
        scripts_dir.mkdir()
        
        if script_type == 'sh':
            src = Path('scripts') / 'bash'
            if src.exists():
                shutil.copytree(src, scripts_dir / 'bash')
                print(f"  ✓ Copied scripts/bash")
        else:  # ps
            src = Path('scripts') / 'powershell'
            if src.exists():
                shutil.copytree(src, scripts_dir / 'powershell')
                print(f"  ✓ Copied scripts/powershell")
        
        # Create .factory/commands directory
        factory_dir = build_dir / ".factory" / "commands"
        factory_dir.mkdir(parents=True)
        
        # Process command templates
        templates_dir = Path('templates') / 'commands'
        for template_file in templates_dir.glob('*.md'):
            process_command_template(template_file, factory_dir, script_type)
        
        print(f"  ✓ Processed {len(list(factory_dir.glob('*.md')))} commands")
        
        # Create zip file
        zip_path = Path.cwd() / f"spec-kit-template-droid-{script_type}-{version}.zip"
        
        print(f"  Creating {zip_path.name}...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(build_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(build_dir)
                    zipf.write(file_path, arcname)
        
        print(f"  ✓ Created {zip_path} ({zip_path.stat().st_size:,} bytes)")
        return zip_path

def process_command_template(template_path, output_dir, script_type):
    """Process a command template and write to output directory"""
    
    content = template_path.read_text()
    name = template_path.stem
    
    # Extract script command from YAML frontmatter
    lines = content.split('\n')
    in_scripts = False
    script_command = None
    
    for i, line in enumerate(lines):
        if line.strip() == 'scripts:':
            in_scripts = True
        elif in_scripts and line.strip().startswith(f'{script_type}:'):
            script_command = line.split(':', 1)[1].strip()
            break
        elif in_scripts and line.strip() and not line.startswith(' '):
            in_scripts = False
    
    if not script_command:
        script_command = f"(Missing script command for {script_type})"
    
    # Process content
    # 1. Replace {SCRIPT} with script command
    processed = content.replace('{SCRIPT}', script_command)
    
    # 2. Replace {ARGS} with $ARGUMENTS
    processed = processed.replace('{ARGS}', '$ARGUMENTS')
    
    # 3. Replace __AGENT__ with droid
    processed = processed.replace('__AGENT__', 'droid')
    
    # 4. Replace path patterns
    processed = processed.replace('memory/', '.specify/memory/')
    processed = processed.replace('scripts/', '.specify/scripts/')
    processed = processed.replace('templates/', '.specify/templates/')
    
    # 5. Remove scripts: and agent_scripts: sections from frontmatter
    lines = processed.split('\n')
    filtered_lines = []
    in_frontmatter = False
    in_scripts_section = False
    dash_count = 0
    
    for line in lines:
        if line.strip() == '---':
            filtered_lines.append(line)
            dash_count += 1
            if dash_count == 1:
                in_frontmatter = True
            else:
                in_frontmatter = False
            continue
        
        if in_frontmatter:
            if line.strip() in ['scripts:', 'agent_scripts:']:
                in_scripts_section = True
                continue
            elif line.strip() and not line.startswith(' ') and ':' in line:
                in_scripts_section = False
            
            if in_scripts_section and line.startswith(' '):
                continue
        
        filtered_lines.append(line)
    
    processed = '\n'.join(filtered_lines)
    
    # Write output file with speckit. prefix
    output_file = output_dir / f"speckit.{name}.md"
    output_file.write_text(processed)

if __name__ == '__main__':
    print("=" * 70)
    print("Building Factory Droid Templates")
    print("=" * 70)
    print()
    
    # Build both sh and ps variants
    for script_type in ['sh', 'ps']:
        try:
            zip_file = create_droid_template(script_type)
            print(f"✓ Successfully built {zip_file.name}")
            print()
        except Exception as e:
            print(f"✗ Error building {script_type} template: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 70)
    print("Build complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Go to: https://github.com/cracked99/fusion-kit/releases/tag/v0.0.21")
    print("2. Click 'Edit release'")
    print("3. Drag and drop these files:")
    print("   - spec-kit-template-droid-sh-v0.0.21.zip")
    print("   - spec-kit-template-droid-ps-v0.0.21.zip")
    print("4. Click 'Update release'")
    print()
    print("After upload, run:")
    print("  specify init my-project --ai droid")
