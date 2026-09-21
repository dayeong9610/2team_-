import dietReviewImg from "../../assets/ep02/diet-reviews.png";

// EP02 SNS 홍보 계정 DM 연출용 - 후기/비포애프터 게시물 예시 이미지
export default function DietReviewPhoto() {
  return (
    <img
      className="ig-review-photo"
      src={dietReviewImg}
      alt="홍보 계정이 보낸 후기 및 비포애프터 예시 이미지"
    />
  );
}
