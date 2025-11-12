import { useState, useEffect } from "react";
import styles from "./toastNotificationRight.module.css";
import Icon from "@leafygreen-ui/icon";
import { Subtitle, Body } from "@leafygreen-ui/typography";

const ToastNotificationRight = ({ text }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
    }, 5000); // Auto-hide after 5 seconds

    return () => clearTimeout(timer);
  }, []);

  if (!visible) return null;

  return (
    <div className={styles.toast}>
        <Icon className={styles.sparkleIcon} glyph="Clock" />
        <Body className={styles.subtitle}> {text}</Body>
    </div>
  );
};

export default ToastNotificationRight;
