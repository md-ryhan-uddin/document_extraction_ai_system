"""
Rotation detection service for document pages.
Detects best orientation automatically (0/90/180/270) before extraction.
"""
import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class RotationDetector:
    """Detects and corrects document rotation"""

    def __init__(self):
        pass

    def detect_rotation(self, image, confidence_threshold=1.2):
        """
        Detect the best rotation angle for the given image.
        Only rotates if there's significant confidence that rotation is needed.

        Args:
            image: PIL Image or numpy array
            confidence_threshold: Minimum ratio of best_score/zero_score to apply rotation (default: 1.2 = 20% better)

        Returns:
            int: Rotation angle (0, 90, 180, 270)
        """
        # Convert PIL Image to numpy array if needed
        if isinstance(image, Image.Image):
            image_np = np.array(image)
        else:
            image_np = image

        # Convert to grayscale
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_np

        # Calculate scores for all orientations
        scores = {}
        for rotation in [0, 90, 180, 270]:
            rotated = self._rotate_image(gray, rotation)
            score = self._calculate_orientation_score(rotated)
            scores[rotation] = score
            logger.debug(f"Rotation {rotation}: score {score:.4f}")

        # Find best rotation
        best_rotation = max(scores, key=scores.get)
        best_score = scores[best_rotation]
        zero_score = scores[0]

        # Only rotate if the best rotation is significantly better than 0 degrees
        if best_rotation != 0:
            if zero_score > 0:
                improvement_ratio = best_score / zero_score
            else:
                improvement_ratio = float('inf') if best_score > 0 else 1.0

            if improvement_ratio < confidence_threshold:
                logger.info(f"Skipping rotation: best={best_rotation}° (score:{best_score:.4f}) is not significantly better than 0° (score:{zero_score:.4f}, ratio:{improvement_ratio:.2f})")
                return 0

        logger.info(f"Detected rotation: {best_rotation}° (score: {best_score:.4f}, 0° score: {zero_score:.4f})")
        return best_rotation

    def _rotate_image(self, image, angle):
        """Rotate image by specified angle"""
        if angle == 0:
            return image
        elif angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return image

    def _calculate_orientation_score(self, gray_image):
        """
        Calculate a score for the current orientation.
        Higher score indicates more likely to be correctly oriented.

        Uses multiple heuristics:
        1. Text line detection (horizontal lines indicate correct orientation)
        2. Edge density in horizontal vs vertical direction
        3. Variance of projections
        """
        # Apply edge detection
        edges = cv2.Canny(gray_image, 50, 150)

        # Calculate horizontal and vertical projections
        h_projection = np.sum(edges, axis=1)  # Sum along rows
        v_projection = np.sum(edges, axis=0)  # Sum along columns

        # Calculate variance of projections
        # Correctly oriented text typically has higher variance in horizontal projection
        h_variance = np.var(h_projection)
        v_variance = np.var(v_projection)

        # Text documents typically have more horizontal structure
        # Calculate the ratio of horizontal to vertical variance
        if v_variance > 0:
            variance_ratio = h_variance / v_variance
        else:
            variance_ratio = h_variance

        # Apply Hough Line Transform to detect lines
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=100,
            minLineLength=100,
            maxLineGap=10
        )

        # Count horizontal lines (lines with small angle from horizontal)
        horizontal_lines = 0
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                # Consider lines within 15 degrees of horizontal
                if angle < 15 or angle > 165:
                    horizontal_lines += 1

        # Combine scores (weighted)
        # More horizontal lines and higher h/v variance ratio indicate better orientation
        score = (variance_ratio * 0.6) + (horizontal_lines * 0.4)

        return score

    def apply_rotation(self, image, angle):
        """
        Apply rotation to image.

        Args:
            image: PIL Image or numpy array
            angle: Rotation angle (0, 90, 180, 270)

        Returns:
            PIL Image: Rotated image
        """
        # Convert to PIL if needed
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        if angle == 0:
            return image
        elif angle == 90:
            return image.rotate(-90, expand=True)
        elif angle == 180:
            return image.rotate(-180, expand=True)
        elif angle == 270:
            return image.rotate(-270, expand=True)

        return image

    def detect_and_correct(self, image):
        """
        Detect rotation and return corrected image.

        Args:
            image: PIL Image or numpy array

        Returns:
            tuple: (corrected_image, detected_angle)
        """
        angle = self.detect_rotation(image)
        corrected = self.apply_rotation(image, angle)
        return corrected, angle
