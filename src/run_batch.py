"""
Run SLAM on multiple sequences
"""
import sys
from config import Config
from dynamic_slam import DynamicSLAM


def run_sequence(sequence_id, start_frame=0, end_frame=None):
    """
    Run SLAM on a single sequence
    
    Args:
        sequence_id: Sequence ID (e.g., "00", "01")
        start_frame: Start frame index
        end_frame: End frame index (None = all frames)
    """
    print("\n" + "=" * 70)
    print(f"RUNNING SEQUENCE {sequence_id}")
    print("=" * 70)
    
    try:
        slam = DynamicSLAM(sequence=sequence_id)
        slam.process_sequence(start_frame=start_frame, end_frame=end_frame)
        
        print(f"\n✓ Sequence {sequence_id} completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error processing sequence {sequence_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run multiple sequences"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Dynamic SLAM on multiple sequences')
    parser.add_argument('--sequences', type=str, nargs='+', default=['00'],
                       help='Sequence IDs to process (e.g., 00 01 02)')
    parser.add_argument('--start', type=int, default=0,
                       help='Start frame')
    parser.add_argument('--end', type=int, default=None,
                       help='End frame (None = all)')
    
    args = parser.parse_args()
    
    sequences = args.sequences
    
    print("=" * 70)
    print("DYNAMIC SLAM - BATCH PROCESSING")
    print("=" * 70)
    print(f"Sequences to process: {', '.join(sequences)}")
    print(f"Frame range: {args.start} to {args.end or 'end'}")
    print("=" * 70)
    
    results = {}
    
    for seq in sequences:
        success = run_sequence(seq, args.start, args.end)
        results[seq] = success
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for seq, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"Sequence {seq}: {status}")
    
    successful = sum(results.values())
    total = len(results)
    
    print(f"\nTotal: {successful}/{total} sequences completed successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()
