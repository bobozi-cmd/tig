from manim import *
from manim.typing import Vector3DLike
from pathlib import Path
from typing import Literal

COMMIT_NODE_R = 0.6
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


class GitMergeFastForwardProcess(Scene):
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
        pos += COMMIT_NODE_INTERVAL
        commit_3_1 = create_commit_node('16dff', pos, 0)
        commit_3_2 = create_commit_node('d6530', pos, -1.5)
        
        arrow_1_0 = Arrow(commit_1.get_left(), commit_0.get_right(), color=GRAY, buff=0.1)
        arrow_2_1 = Arrow(commit_2.get_left(), commit_1.get_right(), color=GRAY, buff=0.1)
        arrow_3_1_2 = Arrow(commit_3_1.get_left(), commit_2.get_right(), color=GRAY, buff=0.1)
        arrow_3_2_2 = Arrow(commit_3_2.get_left(), commit_2.get_right(), color=GRAY, buff=0.1)

        nodes_1 = VGroup(
            commit_0, commit_1, commit_2, commit_3_1, commit_3_2,
            arrow_1_0, arrow_2_1, arrow_3_1_2, arrow_3_2_2
        ).to_edge(LEFT)

        master_branch = create_branch('master')
        master_branch.next_to(commit_2, direction=UP, buff=1)
        arrow_master_2 = Arrow(master_branch.get_bottom(), commit_2.get_top(), color=GRAY, buff=0.1)
        
        HEAD = create_HEAD()
        HEAD.next_to(master_branch, direction=UP, buff=0.8)
        arrow_HEAD_master = Arrow(HEAD.get_bottom(), master_branch.get_top(), color=GRAY, buff=0.1)

        hotfix_branch = create_branch('hotfix')
        hotfix_branch.next_to(commit_3_1, direction=UP, buff=1)
        arrow_hotfix_3_1 = Arrow(hotfix_branch.get_bottom(), commit_3_1.get_top(), color=GRAY, buff=0.1)

        iss53_branch = create_branch('iss53')
        iss53_branch.next_to(commit_3_2, direction=DOWN, buff=1)
        arrow_iss53_3_2 = Arrow(iss53_branch.get_top(), commit_3_2.get_bottom(), color=GRAY, buff=0.1)

        self.play(
            FadeIn(nodes_1), FadeIn(master_branch), 
            FadeIn(arrow_master_2), FadeIn(HEAD), FadeIn(arrow_HEAD_master),
            FadeIn(hotfix_branch), FadeIn(arrow_hotfix_3_1),
            FadeIn(iss53_branch), FadeIn(arrow_iss53_3_2),
        )
        self.wait(1)

        # git merge hotfix (fast forward)
        command = Text('git merge hotfix (fast forward)', color=BLACK, font_size=36).to_edge(DOWN)
        self.add(command)
        self.wait(0.5)

        self.remove(arrow_master_2)
        arrow_master_3_1 = Arrow(master_branch.get_bottom(), commit_3_1.get_top(), color=GRAY, buff=0.1)
        self.play(Create(arrow_master_3_1))
        self.wait(0.5)

        self.remove(HEAD)
        self.remove(arrow_HEAD_master)
        self.remove(master_branch)
        self.remove(arrow_master_3_1)

        master_branch.next_to(hotfix_branch, direction=UP, buff=-0.01)
        HEAD.next_to(master_branch, direction=UP, buff=0.6)
        arrow_HEAD_master = Arrow(HEAD.get_bottom(), master_branch.get_top(), color=GRAY, buff=0.1)
        self.play(FadeIn(master_branch), FadeIn(HEAD), Create(arrow_HEAD_master))
        self.wait(1)


class GitMergeTreeMergeProcess(Scene):
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
        pos += COMMIT_NODE_INTERVAL
        commit_3_1 = create_commit_node('16dff', pos, 0)
        commit_3_2 = create_commit_node('d6530', pos, -1.5)
        pos += COMMIT_NODE_R * 4
        commit_3_2_1 = create_commit_node('8e3b7', pos, -1.5)
        
        arrow_1_0 = Arrow(commit_1.get_left(), commit_0.get_right(), color=GRAY, buff=0.1)
        arrow_2_1 = Arrow(commit_2.get_left(), commit_1.get_right(), color=GRAY, buff=0.1)
        arrow_3_1_2 = Arrow(commit_3_1.get_left(), commit_2.get_right(), color=GRAY, buff=0.1)
        arrow_3_2_2 = Arrow(commit_3_2.get_left(), commit_2.get_right(), color=GRAY, buff=0.1)
        arrow_3_2_1_3_2 = Arrow(commit_3_2_1.get_left(), commit_3_2.get_right(), color=GRAY, buff=0.1)

        nodes_1 = VGroup(
            commit_0, commit_1, commit_2, commit_3_1, commit_3_2, commit_3_2_1,
            arrow_1_0, arrow_2_1, arrow_3_1_2, arrow_3_2_2, arrow_3_2_1_3_2
        ).to_edge(LEFT)

        master_branch = create_branch('master')
        master_branch.next_to(commit_3_1, direction=UP, buff=1)
        arrow_master_3_2 = Arrow(master_branch.get_bottom(), commit_3_1.get_top(), color=GRAY, buff=0.1)
        
        HEAD = create_HEAD()
        HEAD.next_to(master_branch, direction=UP, buff=0.8)
        arrow_HEAD_master = Arrow(HEAD.get_bottom(), master_branch.get_top(), color=GRAY, buff=0.1)

        iss53_branch = create_branch('iss53')
        iss53_branch.next_to(commit_3_2_1, direction=DOWN, buff=0.8)
        arrow_iss53_3_2_1 = Arrow(iss53_branch.get_top(), commit_3_2_1.get_bottom(), color=GRAY, buff=0.1)

        self.play(
            FadeIn(nodes_1), FadeIn(master_branch), 
            FadeIn(arrow_master_3_2), FadeIn(HEAD), FadeIn(arrow_HEAD_master),
            FadeIn(iss53_branch), FadeIn(arrow_iss53_3_2_1),
        )
        self.wait(1)

        # git merge hotfix (three merge)
        command = Text('git merge hotfix (three merge)', color=BLACK, font_size=36).to_edge(DOWN).to_edge(LEFT)
        self.add(command)
        self.wait(0.5)

        common_ancestor = Text('common ancestor', color=BLACK, font_size=24)
        common_ancestor.next_to(commit_2, direction=UP, buff=0.1)

        self.play(
            commit_3_2_1[0].animate.set_fill(RED_A, opacity=1),
            commit_3_1[0].animate.set_fill(RED_A, opacity=1),
            commit_2[0].animate.set_fill(RED, opacity=1),
            FadeIn(common_ancestor),
        )
        self.wait(0.5)

        pos -= COMMIT_NODE_R * 8
        merge_commit = create_commit_node('fec3c', pos, 0)
        arrow_merge_3_1 = Arrow(merge_commit.get_left(), commit_3_1.get_right(), color=GRAY, buff=0.1)
        arrow_merge_3_2_1 = Arrow(merge_commit.get_left(), commit_3_2_1.get_right(), color=GRAY, buff=0.1)
        
        self.play(FadeIn(merge_commit), Create(arrow_merge_3_1), Create(arrow_merge_3_2_1))
        self.wait(0.5)

        self.remove(HEAD)
        self.remove(master_branch)
        self.remove(arrow_HEAD_master)
        self.remove(arrow_master_3_2)

        master_branch.next_to(merge_commit, direction=UP, buff=1)
        arrow_master_merge = Arrow(master_branch.get_bottom(), merge_commit.get_top(), color=GRAY, buff=0.1)
        HEAD.next_to(master_branch, direction=UP, buff=0.8)
        arrow_HEAD_master = Arrow(HEAD.get_bottom(), master_branch.get_top(), color=GRAY, buff=0.1)
        self.play(FadeIn(master_branch), FadeIn(arrow_master_merge), FadeIn(HEAD), FadeIn(arrow_HEAD_master))
        self.wait(1)


if __name__ == "__main__":
    name = 'git-merge-fast-forward'
    target_dir = Path('./animations/output')
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f'{name}.gif'

    with tempconfig({
        'format': 'gif',
        'quality': 'low_quality',
        'media_dir': './media',
        'output_file': name
    }):
        scene = GitMergeFastForwardProcess()
        scene.render()
        default_path = Path(f"./media/videos/480p15/{name}.gif")
        if default_path.exists():
            if target_path.exists():
                target_path.unlink()
            
            default_path.rename(target_path)


    COMMIT_NODE_R = 0.5
    COMMIT_NODE_INTERVAL = COMMIT_NODE_R * 5

    name = 'git-merge-three-merge'
    target_path = target_dir / f'{name}.gif'

    with tempconfig({
        'format': 'gif',
        'quality': 'low_quality',
        'media_dir': './media',
        'output_file': name
    }):
        scene = GitMergeTreeMergeProcess()
        scene.render()
        default_path = Path(f"./media/videos/480p15/{name}.gif")
        if default_path.exists():
            if target_path.exists():
                target_path.unlink()
            
            default_path.rename(target_path)
