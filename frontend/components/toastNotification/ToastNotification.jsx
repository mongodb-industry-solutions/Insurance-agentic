import { useState, useEffect } from "react";
import styles from "./toastNotification.module.css";
import Icon from "@leafygreen-ui/icon";
import { Subtitle, Body } from "@leafygreen-ui/typography";

const ToastNotification = ({ text }) => {
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
        <Icon className={styles.sparkleIcon} glyph="Checkmark" />
        <Body className={styles.subtitle}> {text}</Body>
    </div>
  );
};

export default ToastNotification;
