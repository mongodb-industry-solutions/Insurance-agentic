import Image from "next/image";
import styles from "./userCard.module.css";

const UserCard = ({ name, role, image }) => {
  return (
    <div className={styles.profile}>
      <div className={styles.imageContainer}>
        <Image
          className={styles.image}
          src={image}
          alt="User Profile"
          width={50}
          height={50}
        />
      </div>
      <div className={styles.details}>
        <div className={styles.name}>{name}</div>
        <div className={styles.role}>{role}</div>
      </div>
    </div>
  );
};

export default UserCard;
