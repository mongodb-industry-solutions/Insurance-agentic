"use client";

import { useState, useEffect } from "react";
import styles from "./imageDescriptor.module.css";
import Button from "@leafygreen-ui/button";
import Modal from "@leafygreen-ui/modal";
import UserCard from "../userCard/UserCard";
import { Subtitle, Body } from "@leafygreen-ui/typography";
import Icon from "@leafygreen-ui/icon";
import Badge from "@leafygreen-ui/badge";
import ToastNotification from "../toastNotification/ToastNotification";
import ToastNotificationRight from "../toastNotificationRight/ToastNotificationRight";

const ImageDescriptor = () => {
  const [droppedImage, setDroppedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageDescription, setImageDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [sampleImages, setSampleImages] = useState([]);
  const [showDescription, setShowDescription] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [claimDetails, setClaimDetails] = useState(null);
  const [showSimilarImageSection, setShowSimilarImageSection] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("idle"); // "idle" | "sending" | "uploaded"
  //const [showToastRight, setShowToastRight] = useState(false);

  useEffect(() => {
    const fetchSampleImages = async () => {
      try {
        const response = await fetch("/api/getSampleImages");
        const data = await response.json();
        setSampleImages(data.images);
      } catch (error) {
        console.error("Error fetching sample images:", error);
      }
    };
    fetchSampleImages();
  }, []);

  const handleDragOver = (e) => e.preventDefault();

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      setDroppedImage(file);
      setSelectedImage(null);
      setShowDescription(false);
      const reader = new FileReader();
      reader.onload = (event) => setImagePreview(event.target.result);
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!droppedImage && !selectedImage) {
      alert("Please select or drop an image first.");
      return;
    }

    setLoading(true);
    setUploadStatus("sending"); // Show "SENDING" badge
    setImageDescription(""); // Clear previous description
    setShowDescription(true); // Show description area immediately
    setShowToast(false);
   // setShowToastRight(false);
    setShowSimilarImageSection(false);

    const formData = new FormData();

    if (droppedImage) {
      formData.append("file", droppedImage);
    } else {
      const response = await fetch(selectedImage);
      const blob = await response.blob();
      const file = new File([blob], "selectedImage.jpg", { type: blob.type });
      formData.append("file", file);
    }

    try {
      // Use local Next.js API route instead of direct backend call
      // This avoids SSO authentication issues in Kanopy deployment
      const response = await fetch("/api/image-descriptor", {
        method: "POST",
        body: formData,
      });

      if (!response.body) throw new Error("ReadableStream not supported.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;

        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          console.log("Received chunk:", chunk);

          // Update description directly for the streaming effect
          setImageDescription((prev) => prev + chunk);
        }
      }

      setUploadStatus("uploaded"); // Switch to "UPLOADED FOR REVIEW" badge

      // Show toast notification first
      setTimeout(() => {
        setShowToast(true);
      }, 4000);

      // After description is complete, call the agent
      await runAgent();

    } catch (error) {
      console.error("Error while streaming response:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (claimDetails) {
      setShowSimilarImageSection(true);
    }
  }, [claimDetails]);

  const runAgent = async () => {
    try {
      // Use local Next.js API route instead of direct backend call
      // This avoids SSO authentication issues in Kanopy deployment
      const response = await fetch("/api/run-agent", {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const result = await response.json();
      console.log("Agent result:", result);

      setClaimDetails({
        description: result.description || "No summary available",
        recommendation: result.recommendation || [],
      });

    } catch (error) {
      console.error("Error calling agent:", error);
    }
  };



  const handleImageSelect = (image) => setSelectedImage(image);

  const handleConfirmSelection = () => {
    if (selectedImage) {
      setImagePreview(selectedImage);
      setDroppedImage(null); // Clear the dropped image to prioritize the selected one
      setIsModalOpen(false);
      setShowDescription(false);
      setImageDescription(""); // Clear previous description
    }
  };

  return (
    <div className={styles.content}>
      <div className={styles.imageDescriptorSection}>
        <UserCard name="Luca Napoli" role="Leafy Insurance Customer" image="/assets/eddie.png" />

        <h2>Upload your claim</h2>

        <div className={styles.dragBox} onDragOver={handleDragOver} onDrop={handleDrop}>
          {imagePreview ? (
            <img className={styles.droppedImage} src={imagePreview} alt="Selected" />
          ) : (
            <p className={styles.dragText}>Drag & Drop your image here</p>
          )}
        </div>

        <Button className={styles.uploadBtn} variant="primary" onClick={handleUpload} disabled={loading}>
          {loading ? <div className={styles.spinner}></div> : "Upload and Generate Description"}
        </Button>

        <p className={styles.link} onClick={() => setIsModalOpen(true)}>
          Choose from sample images
        </p>

        {showDescription && (
          <div className={styles.imageDescription}>

            <div className={styles.claimStatusContainer}>
              <Body className={styles.detailTitle}>Claim Status</Body>
              {uploadStatus === "sending" && <Badge variant="yellow">SENDING</Badge>}
              {uploadStatus === "uploaded" && <Badge variant="blue">UPLOADED FOR REVIEW</Badge>}
            </div>

            <div className={styles.imageDescriptionTitle}>
              <Icon className={styles.sparkleIcon} glyph="Sparkle" />
              <Subtitle className={styles.subtitle}>AI generated image description</Subtitle>
            </div>

            <div className={styles.similarDocsContainer}>
              <Body className={styles.similarDoc}>
                {imageDescription || (loading ? "Generating description..." : "")}
              </Body>
            </div>
          </div>
        )}

        {showToast && <ToastNotification text="Your claim is under review and will be assigned shortly" />}

      </div>

      <Modal open={isModalOpen} setOpen={setIsModalOpen}>
        <h3>Choose from the sample images</h3>
        <div className={styles.imageGrid}>
          {sampleImages.map((image, index) => (
            <img
              key={index}
              src={`/sample_photos/${image}`}
              alt={`Sample ${index + 1}`}
              className={selectedImage === `/sample_photos/${image}` ? styles.selectedImage : styles.sampleImage}
              onClick={() => handleImageSelect(`/sample_photos/${image}`)}
            />
          ))}
        </div>
        <Button variant="primary" onClick={handleConfirmSelection} className={styles.confirmButtonContainer}>
          Confirm Selection
        </Button>
      </Modal>

      {/**
      {showToastRight && <ToastNotificationRight text="Incoming claim being processed by agent" />}
 */}
      {showSimilarImageSection && (
        <div className={styles.similarImageSection}>
          <UserCard name="Mark Scout" role="Claim Adjuster" image="/assets/rob.png" />

          <div className={styles.claimContainer}>
            <div className={styles.claimHeader}>
              <Icon className={styles.checkIcon} glyph="Checkmark" />
              <Body>Claim assigned to: <strong>Mark Scout</strong></Body>
            </div>

            <div className={styles.claimDetails}>
              <div className={styles.detailRow}>
                <Body className={styles.detailTitle}>Date created</Body>
                <Body>{new Date().toLocaleDateString()}</Body>
              </div>
              <div className={styles.detailRow}>
                <Body className={styles.detailTitle}>Submitted By</Body>
                <Body>Luca Napoli</Body>
              </div>
              <div className={styles.detailRow}>
                <Body className={styles.detailTitle}>Status</Body>
                <Badge variant="yellow">IN PROGRESS</Badge>
              </div>
            </div>

            <div className={styles.claimSummary}>
              <Subtitle>Accident Summary</Subtitle>
              <Body>{claimDetails ? claimDetails.description : "..."}</Body>
            </div>

            <div className={styles.recommendations}>
              <Subtitle>Recommended next steps</Subtitle>
              <ol>
                {claimDetails?.recommendation?.length > 0 ? (
                  claimDetails.recommendation.map((step, index) => (
                    <li key={index}>
                      <Body>{step}</Body>
                    </li>
                  ))
                ) : (
                  <Body>No recommendations available.</Body>
                )}
              </ol>
            </div>

          </div>
        </div>
      )}
    </div>
  );
};

export default ImageDescriptor;
