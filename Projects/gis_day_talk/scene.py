# %% [markdown]
# # GIS Day Lightning Talk Slides

# %%
import manim as mn
from manim import *
# from manim_slides import Slide

config.media_width = "75%"
config.verbosity = "WARNING"

Text.set_default(font = 'Space Grotesk')


print(mn.__version__)
print(config.frame_width)
print(config.frame_height)
print(config.background_color)
print(config.frame_rate)

# %% [markdown]
# ## Build scene

# %%
# %%manim -qk XarrayOpenData

class XarrayOpenData(Scene):
    def construct(self):
        # Try Text with explicit parameters like the first scene
        hi = Text("Hi there!",  font_size=36, color=WHITE)
        title = Text("Is this you when opening a NetCDF file?",  font_size=36, color=WHITE)
        question = Text("What if there is an easier way?",  font_size=36, color=WHITE)
        cursor = Rectangle(
            color = GREY_A,
            fill_color = GREY_A,
            fill_opacity = 1.0,
            height = 0.5,
            width = 0.2,
        ).move_to(hi[0])
        code = '''import xarray as xr

FILE_PATH = "/mnt/vast/usr/ldas_forecast_data/2025_09.nc"
ds=xr.open_dataset(FILE_PATH, engine="netcdf4")
da = ds['Qair_tavg'].isel(time=0)
ds.close()

import matplotlib.pyplot as plt
da.plot(figsize=(12, 6), cmap='RdBu_r', vmin=-1, vmax=1)
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()
'''
        rendered_code = Code(
            code_string=code, tab_width=4, background="window",
            language="python", paragraph_config=dict(font="Monospace")
        )
        self.play(TypeWithCursor(hi, cursor))
        self.play(Blink(cursor, blinks=2))
        title.to_corner(UP + LEFT)
        self.play(Transform(hi, title))
        self.play(Write(rendered_code))
        self.wait(3)
        cursor = Rectangle(
                    color = GREY_A,
                    fill_color = GREY_A,
                    fill_opacity = 1.0,
                    height = 0.5,
                    width = 0.2,
                ).move_to(question[0])
        self.play(Unwrite(hi), Unwrite(rendered_code, reverse=False))
        self.play(TypeWithCursor(question, cursor))
        self.play(Blink(cursor, blinks=2))
        self.play(FadeOut(question, shift=UP))

# %%
# %%manim -qm WorkFlowExplained

class WorkFlowExplained(ThreeDScene):
    def construct(self):
        # Start with camera pointing straight down (top-down view)
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=0.95)
        
        # Create 3D axes
        grid_size = 6
        plane_color = BLUE
        num_layers = 6
        layer_spacing = 1
        
        # Create ThreeDAxes for proper 3D grid
        axes = ThreeDAxes(
            x_range=[0, grid_size, 1],
            y_range=[0, grid_size, 1],
            z_range=[0, grid_size, 1],
            x_length=grid_size + 3,
            y_length=grid_size + 3,
            z_length=(num_layers - 1) * layer_spacing,
            axis_config={
                "include_tip": False,
                "include_numbers": False,
            }
        )
        time_label = axes.get_z_axis_label(Text("Time-Dimension"), direction=LEFT)
        
        # Helper function to create grid at a specific z-level
        def create_grid_at_z(z_value, opacity=0):
            grid = VGroup()
            num_lines = 6
            for i in range(num_lines + 1):
                # Horizontal lines
                h_line = Line(
                    start=axes.c2p(-grid_size/2, -grid_size/2 + i * grid_size/num_lines, z_value),
                    end=axes.c2p(grid_size/2, -grid_size/2 + i * grid_size/num_lines, z_value),
                    stroke_color=WHITE,
                    stroke_width=1,
                    stroke_opacity=opacity
                )
                grid.add(h_line)
                
                # Vertical lines
                v_line = Line(
                    start=axes.c2p(-grid_size/2 + i * grid_size/num_lines, -grid_size/2, z_value),
                    end=axes.c2p(-grid_size/2 + i * grid_size/num_lines, grid_size/2, z_value),
                    stroke_color=WHITE,
                    stroke_width=1,
                    stroke_opacity=opacity
                )
                grid.add(v_line)
            return grid
        
        # Define plane function for 3D surfaces
        def make_plane_func(z_val):
            return lambda u, v: np.array([u, v, z_val])
        
        # Create first plane as 3D Surface
        first_plane = Surface(
            make_plane_func(0),
            u_range=[-grid_size/2, grid_size/2],
            v_range=[-grid_size/2, grid_size/2],
            resolution=(6, 6),
            fill_color=plane_color,
            fill_opacity=1.0,
            stroke_color=WHITE,
            stroke_width=2,
        )
        
        # Create 2D preview grid (NumberPlane for the intro)
        preview_grid = NumberPlane(
            x_range=[0, 8, 1],
            y_range=[0, 8, 1],
        )
        
        # Title text
        grid_title = Tex("This is a grid")
        grid_title.scale(1.5)
        self.add(preview_grid, grid_title)
        self.play(
            FadeIn(grid_title, shift=DOWN),
            Create(preview_grid, run_time=3, lag_ratio=0.1),
        )
        self.wait()

        # Create 3D grid lines for base layer at z=0
        first_grid = create_grid_at_z(0, opacity=0)
        plane_2d = VGroup(first_plane, first_grid)
        
        self.play(
            DrawBorderThenFill(plane_2d), 
            Unwrite(grid_title),
            FadeOut(preview_grid)
        )
        self.wait(1)
        
        # Pan camera to show it's actually 3D
        self.move_camera(phi=60 * DEGREES, theta=-60 * DEGREES, run_time=3, zoom=0.4)
        
        # Update title
        new_title = Text("Add a data array for each time entry",  font_size=36, color=WHITE).to_corner(LEFT + DOWN)
        self.add_fixed_in_frame_mobjects(new_title)
        self.add(time_label)
        self.play(Write(new_title), Create(axes, run_time=3, lag_ratio=0.1), Write(time_label))
        
        # Create and stack additional layers
        all_layers = VGroup(plane_2d)
        
        for i in range(1, num_layers):
            # Create new plane
            new_plane = Surface(
                make_plane_func(i * layer_spacing),
                u_range=[-grid_size/2, grid_size/2],
                v_range=[-grid_size/2, grid_size/2],
                resolution=(6, 6),
                fill_color=plane_color,
                fill_opacity=1,
                stroke_color=WHITE,
                stroke_width=2,
            )
            
            # Create grid for this layer using axes
            new_grid = create_grid_at_z(i * layer_spacing, opacity=0)
            
            layer = VGroup(new_plane, new_grid)
            all_layers.add(layer)
            
            # Animate stacking
            self.play(FadeIn(layer, shift=UP * 0.3), run_time=0.5)
        
        final_text = MarkupText("Now we have a time series for each grid cell!",  font_size=36, color=WHITE).to_edge(UP)
        self.add_fixed_in_frame_mobjects(final_text)
        self.play(FadeOut(new_title), Write(final_text))

        self.begin_3dillusion_camera_rotation(rate=3)
        self.wait(PI/2)
        self.stop_3dillusion_camera_rotation()

        # Move camera to top-down view
        self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=0.71)
        self.play(Unwrite(time_label), Uncreate(axes), FadeOut(final_text, shift=UP))
        self.wait(1)
        
        # Now highlight one cell on the top layer
        cell_spacing = grid_size / 6
        highlight_pos = [0.5, -0.5, (num_layers - 1) * layer_spacing]
        
        highlight = Square(
            side_length=cell_spacing,
            fill_color=YELLOW,
            fill_opacity=0,
            stroke_color=YELLOW,
            stroke_width=8
        ).move_to(highlight_pos)
        
        transition_text = Text("Let's focus on one grid cell's time series",  font_size=32, color=WHITE)
        transition_text.to_edge(UP)
        self.add_fixed_in_frame_mobjects(transition_text)
        
        self.play(Create(highlight), Write(transition_text, runtime=3, lag_ratios=0.2))
        
        # Animate highlight pulsing
        self.play(highlight.animate.scale(1.2), run_time=0.5)
        self.play(highlight.animate.scale(1/1.2), run_time=0.5)
        self.wait(1)
        
        # Switch to 2D Scene for the rest
        # Create a 2D square at the highlight position
        cell_2d = Square(
            side_length=cell_spacing,
            fill_color=plane_color,
            fill_opacity=0.8,
            stroke_color=WHITE,
            stroke_width=2
        ).move_to(highlight_pos)
        
        # Fade out everything except the highlighted cell
        # We need to transition from 3D to 2D
        self.play(
            FadeIn(cell_2d), 
            FadeOut(all_layers),
            FadeOut(transition_text),
            # 
            run_time=1.5
        )
        self.play(FadeOut(highlight),)
        self.wait(0.5)
        
        # Move to center and scale up
        self.play( cell_2d.animate.move_to(ORIGIN).scale(1.5), run_time=1.5)
        self.wait(0.5)
        
        # Now "expand" this cell into a vertical column showing all time layers
        num_years = 36
        layer_height = 0.1
        
        # Generate random values for the time series
        import random
        time_series_values = [random.random() for _ in range(num_years)]
        
        # Create the column with varying colors
        time_column = VGroup()
        for i, value in enumerate(time_series_values):
            color = interpolate_color(BLUE, RED, value)
            layer = Rectangle(
                width=3,
                height=layer_height,
                fill_color=color,
                fill_opacity=0.8,
                stroke_color=WHITE,
                stroke_width=1
            ).move_to([0, i * layer_height * 1.2 - 2, 0])
            time_column.add(layer)
        
        # # Transform the single cell into the time series column
        # self.play(
        #     FadeOut(cell_2d),
        #     LaggedStart(*[FadeIn(layer, shift=UP * 0.1) for layer in time_column], lag_ratio=0.05),
        #     run_time=2
        # )
        # self.wait(1)
        # Create intermediate stretched cell
        stretched_cell = Rectangle(
            width=cell_spacing,
            height=num_years * layer_height * 1.2,
            fill_color=plane_color,
            fill_opacity=0.8,
            stroke_color=WHITE,
            stroke_width=2
        )

        # Animate: cell stretches, then splits into bars
        self.play(
            Transform(cell_2d, stretched_cell),
            run_time=1.5
        )
        self.play(
            ReplacementTransform(cell_2d, time_column),
            run_time=1.5
        )
        # Add title
        title = Text("Looking at the historical data from 2001-2020",  font_size=32, color=WHITE)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        self.wait(0.5)

        # Add title
        # title = Text("Calculating Tercile Probabilities",  font_size=32, color=WHITE)
        # title.to_edge(UP)
        # self.add_fixed_in_frame_mobjects(title)
        # self.play(Write(title))
        # self.wait(0.5)
        
        # Step 1: Show hindcast layers
        subtitle = Text("We can use it as climatology baseline to calcualte the anomaly",  font_size=24, color=WHITE)
        subtitle.next_to(title, DOWN)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(Write(subtitle))
        self.wait(0.5)
        
        # Store the layers with their values for sorting
        shuffled_layers = [(time_series_values[i], layer) for i, layer in enumerate(time_column)]
        hindcast_layers = time_column
        
        # Step 2: Rank the data
        new_subtitle = Text("Rank from Lowest to Highest",  font_size=24, color=WHITE)
        new_subtitle.next_to(title, DOWN)
        self.play(Transform(subtitle, new_subtitle))
        
        # Now animate sorting
        sort_animations = []
        for i, (value, layer) in enumerate(sorted(shuffled_layers, key=lambda x: x[0])):
            target_y = i * layer_height * 1.2 - 2
            sort_animations.append(layer.animate.move_to([0, target_y, 0]))
        
        self.play(*sort_animations, run_time=2)
        
        # Update hindcast_layers to be in sorted order
        hindcast_layers = VGroup(*[layer for value, layer in sorted(shuffled_layers, key=lambda x: x[0])])
        
        # Shift to the left
        self.play(hindcast_layers.animate.shift(LEFT * 2))
        self.wait(1)
        
        # Step 3: Divide into terciles
        tercile_title = Text("Divide into 3 Categories",  font_size=24, color=WHITE)
        tercile_title.next_to(title, DOWN)
        self.play(Transform(subtitle, tercile_title))
        
        # Add category labels
        below_label = Text("Below\nNormal",  font_size=16, color=BLUE)
        below_label.move_to([-4.5, -1.5, 0])
        self.add_fixed_in_frame_mobjects(below_label)
        
        near_label = Text("Near\nNormal",  font_size=16, color=WHITE)
        near_label.move_to([-4.5, 0, 0])
        self.add_fixed_in_frame_mobjects(near_label)
        
        above_label = Text("Above\nNormal",  font_size=16, color=RED)
        above_label.move_to([-4.5, 1.5, 0])
        self.add_fixed_in_frame_mobjects(above_label)
        
        # Draw dividing lines
        tercile_size = num_years // 3
        div_line1_y = hindcast_layers[tercile_size].get_center()[1]
        div_line2_y = hindcast_layers[2 * tercile_size].get_center()[1]
        
        div_line1 = Line(
            start=[-3.5, div_line1_y, 0],
            end=[-0.5, div_line1_y, 0],
            stroke_color=YELLOW,
            stroke_width=4
        )
        
        div_line2 = Line(
            start=[-3.5, div_line2_y, 0],
            end=[-0.5, div_line2_y, 0],
            stroke_color=YELLOW,
            stroke_width=4
        )
        
        self.play(
            Create(div_line1),
            Create(div_line2),
            Write(below_label),
            Write(near_label),
            Write(above_label)
        )
        self.wait(2)
        
        # Step 4: Bring in forecast ensembles
        forecast_title = Text("Compare Forecast Ensembles",  font_size=24, color=WHITE)
        forecast_title.next_to(title, DOWN)
        self.play(Transform(subtitle, forecast_title))
        
        # Create ensemble members
        ensemble_values = [random.random() for _ in range(7)]
        ensembles = VGroup()
        
        for i, value in enumerate(ensemble_values):
            color = interpolate_color(BLUE, RED, value)
            ensemble = Rectangle(
                width=0.3,
                height=layer_height,
                fill_color=color,
                fill_opacity=0.9,
                stroke_color=YELLOW,
                stroke_width=2
            ).shift(RIGHT * 2 + UP * (i * 0.15 - 1))
            ensembles.add(ensemble)
        
        self.play(LaggedStart(*[FadeIn(e, shift=LEFT) for e in ensembles], lag_ratio=0.1))
        self.wait(1)
        
        # Step 5: Categorize ensembles
        categorize_title = Text("Categorize Each Ensemble",  font_size=24, color=WHITE)
        categorize_title.next_to(title, DOWN)
        self.play(Transform(subtitle, categorize_title))
        
        # Count categories
        below_count = sum(1 for v in ensemble_values if v < 0.33)
        near_count = sum(1 for v in ensemble_values if 0.33 <= v < 0.67)
        above_count = sum(1 for v in ensemble_values if v >= 0.67)
        
        # Move ensembles to their categories
        animations = []
        below_pos = 0
        near_pos = 0
        above_pos = 0
        
        for i, (ensemble, value) in enumerate(zip(ensembles, ensemble_values)):
            if value < 0.33:
                target = [-2, -1.5 + below_pos * 0.15, 0]
                below_pos += 1
            elif value < 0.67:
                target = [-2, 0 + near_pos * 0.15, 0]
                near_pos += 1
            else:
                target = [-2, 1.5 + above_pos * 0.15, 0]
                above_pos += 1
            animations.append(ensemble.animate.move_to(target))
        
        self.play(*animations, run_time=2)
        self.wait(1)
        
        # Step 6: Calculate probabilities
        prob_title = Text("Calculate Probabilities",  font_size=24, color=WHITE)
        prob_title.next_to(title, DOWN)
        self.play(Transform(subtitle, prob_title))
        
        # Show probability text on the right side
        prob_above = Text(f"Above: {above_count}/7 = {above_count/10:.0%}", 
                          font_size=20, color=RED)
        prob_above.next_to(hindcast_layers, RIGHT).shift(RIGHT * 0.5 + UP * 1)
        self.add_fixed_in_frame_mobjects(prob_above)

        prob_near = Text(f"Near: {near_count}/7 = {near_count/7:.0%}", 
                         font_size=20, color=WHITE)
        prob_near.next_to(prob_above, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(prob_near)
        
        prob_below = Text(f"Below: {below_count}/7 = {below_count/7:.0%}", 
                          font_size=20, color=BLUE)
        prob_below.next_to(prob_near, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(prob_below)
        
        self.play(
            Write(prob_above),
            Write(prob_near),
            Write(prob_below),
            #Indicate(prob_near)
        )
        self.wait()
        self.play(
            Indicate(prob_below)
        )
        self.wait(PI/2)

# %% [markdown]
# ## Build background canvas

# %%
# # %%manim -qm HydroViewerBackground

# class HydroViewerBackground(Scene):
#     def construct(self):
#         # AmazonHydroViewer brutalist color palette
#         WHITE = "#ffffff"
#         BLACK = "#000000"
#         LIGHT_GRAY = "#f5f5f5"
        
#         # Border width from the CSS
#         BORDER_WIDTH = 4  # 2px scaled up for Manim
        
#         # Set white background for brutalist look
#         self.camera.background_color = BLACK
        
#         # Create bold black border frame
#         border = Rectangle(
#             width=config.frame_width - 0.4,
#             height=config.frame_height - 0.4,
#             stroke_color=WHITE,
#             stroke_width=BORDER_WIDTH,
#             fill_opacity=0
#         )
        
#         # Add light gray accent panel at top (header area)
#         header = Rectangle(
#             width=config.frame_width - 0.4,
#             height=1.5,
#             fill_color=BLACK,
#             fill_opacity=1,
#             stroke_color=WHITE,
#             stroke_width=BORDER_WIDTH
#         ).to_edge(UP, buff=0.2)
        
#         # Create offset shadow effect for header (brutalist micro-interaction)
#         header_shadow = Rectangle(
#             width=config.frame_width - 0.4,
#             height=1.5,
#             fill_color=BLACK,
#             fill_opacity=1,
#             stroke_width=0
#         ).to_edge(UP, buff=0.2).shift(RIGHT * 0.05 + DOWN * 0.05)
        
#         # Add title with Space Grotesk font (bold, uppercase)
#         title = Text(
#             "AMAZONHYDROVIEWER",
#               # Using the actual Space Grotesk font!
#             font_size=48,
#             color=WHITE,
#             #weight=REGULAR
#         ).move_to(header.get_center())
        
#         # Add content area with light gray background
#         content_bg = Rectangle(
#             width=config.frame_width - 0.8,
#             height=config.frame_height - 2.5,
#             fill_color=WHITE,
#             fill_opacity=0.3,
#             stroke_width=0
#         ).shift(DOWN * 0.3)
        
#         # Add decorative elements with offset shadow
#         card1 = Rectangle(
#             width=5,
#             height=2,
#             fill_color=BLACK,
#             fill_opacity=1,
#             stroke_color=WHITE,
#             stroke_width=BORDER_WIDTH
#         ).shift(LEFT * 3 + DOWN * 1)
        
#         card1_shadow = Rectangle(
#             width=5,
#             height=2,
#             fill_color=WHITE,
#             fill_opacity=1,
#             stroke_width=0
#         ).shift(LEFT * 3 + DOWN * 1 + RIGHT * 0.08 + DOWN * 0.08)
        
#         card2 = Rectangle(
#             width=5,
#             height=2,
#             fill_color=BLACK,
#             fill_opacity=1,
#             stroke_color=WHITE,
#             stroke_width=BORDER_WIDTH
#         ).shift(RIGHT * 3 + DOWN * 1)
        
#         card2_shadow = Rectangle(
#             width=5,
#             height=2,
#             fill_color=WHITE,
#             fill_opacity=1,
#             stroke_width=0
#         ).shift(RIGHT * 3 + DOWN * 1 + RIGHT * 0.08 + DOWN * 0.08)
        
#         # Add subtitle with Space Grotesk
#         subtitle = Text(
#             "GIS Day 2024",
#             
#             font_size=24,
#             color=WHITE,
#             #weight=REGULAR
#         ).next_to(header, DOWN, buff=0.5)
        
#         # Assemble scene
#         self.add(content_bg)
#         self.add(card1_shadow, card1)
#         self.add(card2_shadow, card2)
#         self.add(header_shadow, header, border)
        
#         # Animate title in
#         self.play(Write(title))
#         self.play(
#             FadeIn(subtitle, shift=DOWN * 0.1),
#             run_time=1
#         )
#         self.wait(2)


