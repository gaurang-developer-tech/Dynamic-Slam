"""
Trajectory evaluation script using EVO library
Compares estimated trajectory with ground truth
"""
import os
import sys
import numpy as np
from config import Config


def evaluate_trajectory_evo(trajectory_file, ground_truth_file, sequence_id):
    """
    Evaluate trajectory using EVO library
    
    Args:
        trajectory_file: Path to estimated trajectory
        ground_truth_file: Path to ground truth trajectory
        sequence_id: Sequence identifier
    """
    try:
        from evo.core import sync
        from evo.core.trajectory import PoseTrajectory3D
        from evo.tools import file_interface
        from evo.core import metrics
        from evo.core.metrics import PoseRelation, Unit
        import evo.main_ape as main_ape
        import evo.main_rpe as main_rpe
    except ImportError:
        print("ERROR: EVO library not installed!")
        print("Install with: pip install evo")
        return
    
    print("\n" + "=" * 60)
    print(f"Evaluating Trajectory for Sequence {sequence_id}")
    print("=" * 60)
    
    # Load trajectories
    print(f"\nLoading trajectories...")
    print(f"  Estimated: {trajectory_file}")
    print(f"  Ground Truth: {ground_truth_file}")
    
    traj_est = file_interface.read_kitti_poses_file(trajectory_file)
    traj_ref = file_interface.read_kitti_poses_file(ground_truth_file)
    
    # Synchronize trajectories (in case of different lengths)
    traj_ref, traj_est = sync.associate_trajectories(traj_ref, traj_est)
    
    print(f"  Trajectory length: {len(traj_est.poses_se3)} poses")
    
    # Calculate APE (Absolute Pose Error)
    print("\n" + "-" * 60)
    print("Absolute Pose Error (APE)")
    print("-" * 60)
    
    ape_metric = metrics.APE(metrics.PoseRelation.translation_part)
    ape_metric.process_data((traj_ref, traj_est))
    
    ape_stats = ape_metric.get_all_statistics()
    print(f"  Mean:   {ape_stats['mean']:.4f} m")
    print(f"  Median: {ape_stats['median']:.4f} m")
    print(f"  Std:    {ape_stats['std']:.4f} m")
    print(f"  Min:    {ape_stats['min']:.4f} m")
    print(f"  Max:    {ape_stats['max']:.4f} m")
    print(f"  RMSE:   {ape_stats['rmse']:.4f} m")
    
    # Calculate RPE (Relative Pose Error)
    print("\n" + "-" * 60)
    print("Relative Pose Error (RPE)")
    print("-" * 60)
    
    rpe_metric = metrics.RPE(
        metrics.PoseRelation.translation_part,
        delta=1.0,
        delta_unit=Unit.frames
    )
    rpe_metric.process_data((traj_ref, traj_est))
    
    rpe_stats = rpe_metric.get_all_statistics()
    print(f"  Mean:   {rpe_stats['mean']:.4f} m")
    print(f"  Median: {rpe_stats['median']:.4f} m")
    print(f"  Std:    {rpe_stats['std']:.4f} m")
    print(f"  Min:    {rpe_stats['min']:.4f} m")
    print(f"  Max:    {rpe_stats['max']:.4f} m")
    print(f"  RMSE:   {rpe_stats['rmse']:.4f} m")
    
    # Save results
    results_file = Config.get_results_path(f"evo_results_seq{sequence_id}.txt")
    with open(results_file, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write(f"EVO Evaluation Results - Sequence {sequence_id}\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("Absolute Pose Error (APE):\n")
        f.write(f"  Mean:   {ape_stats['mean']:.4f} m\n")
        f.write(f"  Median: {ape_stats['median']:.4f} m\n")
        f.write(f"  Std:    {ape_stats['std']:.4f} m\n")
        f.write(f"  RMSE:   {ape_stats['rmse']:.4f} m\n\n")
        
        f.write("Relative Pose Error (RPE):\n")
        f.write(f"  Mean:   {rpe_stats['mean']:.4f} m\n")
        f.write(f"  Median: {rpe_stats['median']:.4f} m\n")
        f.write(f"  Std:    {rpe_stats['std']:.4f} m\n")
        f.write(f"  RMSE:   {rpe_stats['rmse']:.4f} m\n")
    
    print(f"\nResults saved to: {results_file}")
    
    # Generate plots using EVO
    try:
        import matplotlib.pyplot as plt
        from evo.tools import plot
        
        # Plot trajectory
        print("\nGenerating EVO plots...")
        
        fig = plt.figure(figsize=(12, 10))
        
        # 2D plot (top view)
        ax = plot.prepare_axis(fig, plot.PlotMode.xy)
        plot.traj(ax, plot.PlotMode.xy, traj_ref, '--', 'gray', 'Ground Truth')
        plot.traj(ax, plot.PlotMode.xy, traj_est, '-', 'blue', 'Estimated')
        ax.legend()
        ax.set_title(f'Trajectory Comparison - Sequence {sequence_id}')
        
        plot_file = Config.get_results_path(f"evo_trajectory_seq{sequence_id}.png")
        plt.savefig(plot_file, dpi=150, bbox_inches='tight')
        print(f"Trajectory plot saved to: {plot_file}")
        plt.close()
        
        # APE plot
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        plot.error_array(
            ax, ape_metric.error, 
            name='APE',
            title=f'Absolute Pose Error - Sequence {sequence_id}',
            xlabel='Frame'
        )
        
        ape_plot_file = Config.get_results_path(f"evo_ape_seq{sequence_id}.png")
        plt.savefig(ape_plot_file, dpi=150, bbox_inches='tight')
        print(f"APE plot saved to: {ape_plot_file}")
        plt.close()
        
        # RPE plot
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        plot.error_array(
            ax, rpe_metric.error,
            name='RPE',
            title=f'Relative Pose Error - Sequence {sequence_id}',
            xlabel='Frame'
        )
        
        rpe_plot_file = Config.get_results_path(f"evo_rpe_seq{sequence_id}.png")
        plt.savefig(rpe_plot_file, dpi=150, bbox_inches='tight')
        print(f"RPE plot saved to: {rpe_plot_file}")
        plt.close()
        
    except Exception as e:
        print(f"Warning: Could not generate EVO plots: {e}")
    
    print("\n" + "=" * 60)
    print("Evaluation complete!")
    print("=" * 60)


def main():
    """Main entry point for trajectory evaluation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate SLAM trajectory using EVO')
    parser.add_argument('--sequence', type=str, default=Config.SEQUENCE,
                       help='Sequence ID (default: 00)')
    parser.add_argument('--trajectory', type=str, default=None,
                       help='Path to estimated trajectory file')
    parser.add_argument('--ground_truth', type=str, default=None,
                       help='Path to ground truth file')
    
    args = parser.parse_args()
    
    # Get file paths
    if args.trajectory is None:
        trajectory_file = Config.get_results_path(f"trajectory_seq{args.sequence}.txt")
    else:
        trajectory_file = args.trajectory
    
    if args.ground_truth is None:
        gt_file = Config.get_poses_path(args.sequence)
    else:
        gt_file = args.ground_truth
    
    # Check if files exist
    if not os.path.exists(trajectory_file):
        print(f"ERROR: Trajectory file not found: {trajectory_file}")
        print("Run the SLAM system first to generate the trajectory.")
        return
    
    if not os.path.exists(gt_file):
        print(f"ERROR: Ground truth file not found: {gt_file}")
        return
    
    # Evaluate
    evaluate_trajectory_evo(trajectory_file, gt_file, args.sequence)


if __name__ == "__main__":
    main()
