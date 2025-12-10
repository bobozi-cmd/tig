from manim import *
from manim.typing import Vector3DLike
from pathlib import Path
from typing import Literal

COMMIT_NODE_R = 0.8
COMMIT_NODE_INTERVAL = COMMIT_NODE_R * 6

BRANCH_HEIGHT = 0.5
BRANCH_WIDTH = 2.0

def create_commit_node(sha1, x, y):
    circle = Circle(radius=COMMIT_NODE_R, color=BLACK, fill_color=GRAY, fill_opacity=1)
    circle.move_to([x, y, 0])

    sha1_text = Text(sha1, font_size=18, color=BLACK)
    sha1_text.move_to(circle.get_center())

    return VGroup(circle, sha1_text)

def create_branch(name: str):
    branch = Rectangle(height=BRANCH_HEIGHT, width=BRANCH_WIDTH, color=BLACK, fill_color=RED, fill_opacity=0.2)
    branch_text = Text(name, font_size=24, color=BLACK)
    branch_text.move_to(branch.get_center())

    return VGroup(branch, branch_text)

def create_HEAD():
    branch = Rectangle(height=BRANCH_HEIGHT, width=BRANCH_WIDTH, color=BLACK, fill_color=YELLOW, fill_opacity=0.2)
    branch_text = Text('HEAD', font_size=24, color=BLACK)
    branch_text.move_to(branch.get_center())

    return VGroup(branch, branch_text)

class GitCommitProcess(Scene):
    def construct(self):
        # 设置背景颜色
        self.camera.background_color = WHITE

        # 创建初始状态
        pos = 0
        commit_0 = create_commit_node('98ca9', pos, 0)
        pos += COMMIT_NODE_INTERVAL
        commit_1 = create_commit_node('34ac2', pos, 0)
        pos += COMMIT_NODE_INTERVAL
        commit_2 = create_commit_node('f30ab', pos, 0)
        
        arrow_1_0 = Arrow(commit_1.get_left(), commit_0.get_right(), color=GRAY, buff=0.1)
        arrow_2_1 = Arrow(commit_2.get_left(), commit_1.get_right(), color=GRAY, buff=0.1)

        nodes_1 = VGroup(
            commit_0, commit_1, commit_2,
            arrow_1_0, arrow_2_1
        ).to_edge(LEFT)

        master_branch = create_branch('master')
        master_branch.next_to(commit_2, direction=UP, buff=1)
        arrow_master_2 = Arrow(master_branch.get_bottom(), commit_2.get_top(), color=GRAY, buff=0.1)
        
        HEAD = create_HEAD()
        HEAD.next_to(master_branch, direction=UP, buff=0.8)
        arrow_HEAD_master = Arrow(HEAD.get_bottom(), master_branch.get_top(), color=GRAY, buff=0.1)

        self.play(FadeIn(nodes_1), FadeIn(master_branch), FadeIn(arrow_master_2), FadeIn(HEAD), FadeIn(arrow_HEAD_master))
        self.wait(1)

        # git branch test
        command = Text('git branch test', color=BLACK).to_edge(DOWN)
        self.add(command)
        self.wait(0.5)

        test_branch = create_branch('test')
        test_branch.next_to(commit_2, direction=DOWN, buff=1)
        arrow_test_2 = Arrow(test_branch.get_top(), commit_2.get_bottom(), color=GRAY, buff=0.1)

        self.play(FadeIn(test_branch), Create(arrow_test_2))
        self.wait(1)

        # git branch feature 34ac2
        self.remove(command)
        command = Text('git branch feature 34ac2', color=BLACK).to_edge(DOWN)
        self.add(command)
        self.wait(0.5)

        feature_branch = create_branch('feature')
        feature_branch.next_to(commit_1, direction=UP, buff=1)
        arrow_feature_1 = Arrow(feature_branch.get_bottom(), commit_1.get_top(), color=GRAY, buff=0.1)

        self.play(FadeIn(feature_branch), Create(arrow_feature_1))
        self.wait(1)

        # git checkout feature
        self.remove(command)
        command = Text('git checkout feature', color=BLACK).to_edge(DOWN)
        self.add(command)
        self.wait(0.5)

        self.remove(HEAD)
        self.remove(arrow_HEAD_master)
        HEAD.next_to(feature_branch, direction=UP, buff=0.8)
        arrow_HEAD_feature = Arrow(HEAD.get_bottom(), feature_branch.get_top(), color=GRAY, buff=0.1)
        self.play(FadeIn(HEAD), Create(arrow_HEAD_feature))
        self.wait(1)

        # git branch -d test
        self.remove(command)
        command = Text('git branch -d test', color=BLACK).to_edge(DOWN)
        self.add(command)
        self.wait(0.5)

        self.play(Uncreate(arrow_test_2), FadeOut(test_branch))
        self.wait(1)

if __name__ == "__main__":
    name = 'git-branch'
    target_dir = Path('./animations/output')
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f'{name}.gif'

    with tempconfig({
        'format': 'gif',
        'quality': 'low_quality',
        'media_dir': './media',
        'output_file': name
    }):
        scene = GitCommitProcess()
        scene.render()
        default_path = Path(f"./media/videos/480p15/{name}.gif")
        if default_path.exists():
            if target_path.exists():
                target_path.unlink()
            
            default_path.rename(target_path)
