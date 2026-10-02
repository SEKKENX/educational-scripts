"""Pixel regressions for stale animation frames (no GUI window required).

Run from SCRIPTS CUANTICA: python -m unittest discover -s tests -v
"""
import io
import sys
import unittest
from pathlib import Path

import matplotlib
matplotlib.use('Agg', force=True)

import numpy as np
from matplotlib.backend_bases import MouseEvent, ResizeEvent

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from campos_cuanticos import Simulator, SCENE_DURATIONS


class AnimationRenderingTests(unittest.TestCase):
    def setUp(self):
        self.sim = Simulator(animate=True)
        self.sim.running = False
        self.sim.fig.canvas.draw()

    def tearDown(self):
        self.sim.plt.close(self.sim.fig)

    def assert_clean_frame(self):
        """Compare the displayed frame to an independently rebuilt clean frame.

        Layout-only checks and savefig miss ghosts baked into a blit background.
        This checks the actual on-screen buffer, including changing numbers.
        """
        sim = self.sim
        canvas = sim.fig.canvas
        actual = np.asarray(canvas.buffer_rgba()).copy()
        with canvas.callbacks.blocked(signal='draw_event'):
            canvas.draw()
        for artist in sorted(sim.artists(), key=lambda item: item.get_zorder()):
            artist.axes.draw_artist(artist)
        expected = np.asarray(canvas.buffer_rgba()).copy()
        differences = int(np.count_nonzero(np.any(actual != expected, axis=2)))
        self.assertEqual(differences, 0,
                         f'{differences} pixels differ from a clean frame in '
                         f'scene {sim.scene_index} at t={sim.seconds:.3f}')

    def frame_at(self, seconds):
        self.sim.seconds = seconds
        self.sim.render()
        self.sim.animation._step()
        self.assert_clean_frame()

    def test_refresh_before_first_timer_frame(self):
        self.sim.refresh()
        self.frame_at(1.5)
        self.frame_at(2.8)

    def test_every_chapter_after_manual_selection(self):
        for scene, seconds in [(0, 1.5), (4, 3.), (1, 6.), (2, 9.), (3, 7.)]:
            with self.subTest(scene=scene):
                self.sim.select_scene(scene)
                self.assert_clean_frame()
                self.frame_at(seconds)
                self.frame_at(seconds+.6)

    def test_actual_button_events_and_continuous_playback(self):
        canvas = self.sim.fig.canvas
        for scene in (4, 0):
            button = self.sim.controls[scene]
            box = button.ax.get_window_extent()
            x, y = (box.x0+box.x1)/2, (box.y0+box.y1)/2
            for event in ('button_press_event', 'button_release_event'):
                MouseEvent(event, canvas, x, y, button=1)._process()
            self.assertEqual(self.sim.scene_index, scene)
            # Do not rebuild a reference between frames: check real accumulated
            # display state after a sustained sequence of timer callbacks.
            for seconds in np.linspace(.05, 5., 90):
                self.sim.seconds = seconds
                self.sim.render()
                self.sim.animation._step()
            self.assert_clean_frame()

    def test_restart_and_pause_controls(self):
        self.sim.select_scene(4)
        self.frame_at(3.)
        self.sim.toggle()
        self.sim.toggle()
        self.assertFalse(self.sim.running)
        self.frame_at(4.)
        self.sim.restart()
        self.assert_clean_frame()
        self.frame_at(2.)
        self.sim.toggle_auto()
        self.frame_at(2.5)

    def test_automatic_chapter_and_state_changes(self):
        self.sim.select_scene(0)
        for scene, duration in enumerate(SCENE_DURATIONS):
            self.assertEqual(self.sim.scene_index, scene)
            self.frame_at(duration-.02)
            self.sim.advance(.04)
            self.sim.animation._step()
            self.assert_clean_frame()
        self.assertEqual(self.sim.scene_index, 0)
        self.sim.select_scene(2)
        for seconds in (3.99, 4.01, 8.01, 12.01, 16.01):
            self.frame_at(seconds)

    def test_resize_redraw_and_speed_control(self):
        for width, height, dpi in [(9, 5.4, 100), (12, 6.5, 144), (15, 9, 100)]:
            with self.subTest(size=(width, height, dpi)):
                self.sim.fig.set_size_inches(width, height)
                self.sim.fig.set_dpi(dpi)
                ResizeEvent('resize_event', self.sim.fig.canvas)._process()
                self.sim.fig.canvas.draw()
                self.sim.select_scene(4)
                self.frame_at(2.)
                self.sim.speed.set_val(1.5)
                self.frame_at(3.)
                self.sim.fig.canvas.draw()
                self.frame_at(4.)

    def test_image_export_does_not_pollute_next_frame(self):
        self.sim.select_scene(4)
        self.frame_at(1.)
        with io.BytesIO() as output:
            self.sim.fig.savefig(output, format='png', dpi=140)
        self.sim.fig.canvas.draw()
        self.frame_at(3.)


if __name__ == '__main__':
    unittest.main()
