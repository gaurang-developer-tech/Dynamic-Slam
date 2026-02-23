"""
Simple run script for Dynamic SLAM
Quick entry point with command-line arguments
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dynamic_slam import DynamicSLAM
from config import Config


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Dynamic SLAM - Monocular Visual Odometry with Dynamic Object Filtering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run on default sequence (00)
  python run.py
  
  # Run on specific sequence
  python run.py --sequence 01
  
  # Process limited frames
  python run.py --start 0 --end 100
  
  # Quick demo (first 50 frames)
  python run.py --demo
        """
    )
    
    parser.add_argument('--sequence', type=str, default='00',
                       help='Sequence ID (e.g., 00, 01, 02)')
    parser.add_argument('--start', type=int, default=0,
                       help='Start frame index')
    parser.add_argument('--end', type=int, default=None,
                       help='End frame index (None = process all frames)')
    parser.add_argument('--demo', action='store_true',
                       help='Run quick demo (first 50 frames)')
    parser.add_argument('--evaluate', action='store_true',
                       help='Run trajectory evaluation after processing')
    
    args = parser.parse_args()
    
    # Demo mode
    if args.demo:
        print("\n🚀 Running in DEMO mode (first 50 frames)")
        args.end = 50
    
    # Update config
    Config.SEQUENCE = args.sequence
    
    print("\n" + "=" * 70)
    print("DYNAMIC SLAM")
    print("=" * 70)
    print(f"Sequence: {args.sequence}")
    print(f"Frame range: {args.start} to {args.end or 'end'}")
    print("=" * 70 + "\n")
    
    # Run SLAM
    try:
        slam = DynamicSLAM(sequence=args.sequence)
        slam.process_sequence(start_frame=args.start, end_frame=args.end)
        
        print("\n✓ SLAM processing completed successfully!")
        
        # Run evaluation if requested
        if args.evaluate:
            print("\nRunning trajectory evaluation...")
            from evaluate_trajectory import evaluate_trajectory_evo
            
            trajectory_file = Config.get_results_path(f"trajectory_seq{args.sequence}.txt")
            gt_file = Config.get_poses_path(args.sequence)
            
            if os.path.exists(trajectory_file) and os.path.exists(gt_file):
                evaluate_trajectory_evo(trajectory_file, gt_file, args.sequence)
            else:
                print("⚠ Cannot evaluate: trajectory or ground truth file not found")
        
        print(f"\n📁 Results saved to: {Config.RESULTS_DIR}")
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
