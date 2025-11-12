"use client";

import UserProfile from "../userProfile/UserProfile";
import styles from "./navbar.module.css";
import Image from "next/image";
import { useState } from "react";
import InfoWizard from "../InfoWizard/InfoWizard";

const Navbar = () => {
  const [openHelpModal, setOpenHelpModal] = useState(false);
  return (
    <nav className={styles.navbar}>
      <div className={styles.logo}>
        <Image src="/assets/logo.png" alt="Logo" width={200} height={40} />{" "}
      </div>
      <InfoWizard
        open={openHelpModal}
        setOpen={setOpenHelpModal}
        tooltipText="Tell me more!"
        iconGlyph="Wizard"

        sections={[
          {
            heading: "Instructions and Talk Track",
            content: [
              {
                heading: "Agentic AI in Insurance",
                body: "Efficient claim processing is critical for insurers, with timely resolution and information transparency being key to maintaining positive customer relationships and satisfaction. AI is helping insurers make sense of vast amounts of data faster and in real-time, from unstructured content like police reports and dashboard camera footage to written descriptions and vehicle telemetry. Through capabilities like natural language processing, image classification, and vector embedding, AI enables insurers to tame the flood of claim-related data, generate accurate catastrophe impact assessments, expedite claim routing with richer metadata, avoid litigation through better analysis, and prevent losses altogether through predictive risk assessment.",
              },
              {
                heading: "How to Demo",
                body: [
                  "Drag and drop an image into the box or select one from the sample images.",
                  "Press 'Upload and Generate Description'.",
                  "The LLM will generate a description of the image.",
                  "The description kicks off the agentic workflow.",
                  "The agent will then use the description to find relevant guidelines.",
                  "The agent will then use the guidelines to generate a recommendation and assign a work order to a claim adjuster.",
                  "The agent will then persist the recommendation and work order to MongoDB.",
                ],
              },
            ],
          },
          {
            heading: "Behind the Scenes",
            content: [
              {
                heading: "Workflow",
                images: [
                  {
                    src: "assets/flow.png"
                  },
                  {
                    
                  },
                ],
              },
            ],
          },
          {
            heading: "Why MongoDB?",
            content: [
              {
                heading: "Operational and Vector Database Combined",
                body: "MongoDB stores vectors alongside operational data, eliminating the need to having two separate solutions. Enabling features such as pre-filtering.",

              },
              {
                heading: "Tools as documents",
                body: "You can store tool definitions, prompts, workflows, and even past runs in MongoDB as JSON documents. That makes it easier to version, audit, and evolve your agent capabilities over time.",

              },
              {
                heading: "Flexible Schema for Evolving Agent Workflows",
                body: "Agents often work with semi-structured or rapidly evolving data (e.g., user prompts, metadata, tool outputs, embeddings). MongoDB’s document model lets you easily store and update that kind of dynamic data without rigid schemas getting in the way.",

              },
            ],
          },
        ]}
      />
      {/*<div className={styles.user}>
        <UserProfile />
      </div>
      */}
    </nav>
  );
};

export default Navbar;
