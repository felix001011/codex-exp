import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

# Parameters
n_rows, n_cols = 16, 16
start_period = 0.3  # seconds
end_period = 0.001  # seconds
cycles = 40
frames_per_cycle = n_rows

# Periods for each frame
scan_periods = np.logspace(np.log10(start_period), np.log10(end_period), cycles * frames_per_cycle)
# Linger at the fastest period for a bit
linger_cycles = 10
scan_periods = np.concatenate([scan_periods, np.full(linger_cycles * n_rows, end_period)])

# Threshold where flicker should disappear (60 Hz -> ~16.7 ms)
flicker_threshold = 0.0167

# Total frames includes extra time to keep all LEDs lit at the end
all_lit_frames = 200  # 2 seconds at 10 ms
n_frames = len(scan_periods) + all_lit_frames

led_grid = np.zeros((n_rows, n_cols))

fig, ax = plt.subplots(figsize=(6, 6))
im = ax.imshow(led_grid, cmap='Greens', vmin=0, vmax=1)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title('PM LED Display Row Scanning\n(Frame period decreases from 0.3s to 1ms)')

period_text = ax.text(0.5, 1.05, '', transform=ax.transAxes,
                      ha='center', va='bottom', fontsize=12)
flicker_text = ax.text(0.5, -0.08, '', transform=ax.transAxes,
                       ha='center', va='top', fontsize=14, color='red')

# We'll update the timer interval from within the animation function
ani = None

def update(frame):
    global ani
    if frame < len(scan_periods):
        period = scan_periods[frame]
        row = frame % n_rows
        led_grid[:, :] = 0
        led_grid[row, :] = 1
        im.set_data(led_grid)
        period_text.set_text(f'Frame period: {period*1000:.1f} ms')
        flicker_text.set_text(
            'Scan is now too fast to see flicker (flicker fusion)'
            if period <= flicker_threshold else 'Flicker is visible')
        # Schedule next frame with the upcoming period
        if frame < len(scan_periods) - 1:
            ani.event_source.interval = scan_periods[frame + 1] * 1000
    else:
        led_grid[:, :] = 1
        im.set_data(led_grid)
        period_text.set_text('All rows ON (persistence of vision)')
        flicker_text.set_text('')
        ani.event_source.interval = 10  # steady 10 ms
        if frame == n_frames - 1:
            ani.event_source.stop()
    return [im, period_text, flicker_text]

ani = animation.FuncAnimation(
    fig,
    update,
    frames=n_frames,
    interval=scan_periods[0] * 1000,
    blit=True,
    repeat=False,
)

plt.tight_layout()
plt.show()
