// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-publications",
          title: "publications",
          description: "My research publications.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-cv",
          title: "cv",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "news-selected-for-an-exchange-program-and-studied-at-technical-university-of-munich-tum",
          title: '🌍 Selected for an exchange program and studied at Technical University of Munich...',
          description: "",
          section: "News",},{id: "news-graduated-from-postech-with-a-b-s-degree-in-computer-science-and-engineering",
          title: '🎓 Graduated from POSTECH with a B.S. degree in Computer Science and Engineering....',
          description: "",
          section: "News",},{id: "news-started-ph-d-program-in-computer-science-and-engineering-at-postech",
          title: '🚀 Started Ph.D. program in Computer Science and Engineering at POSTECH.',
          description: "",
          section: "News",},{id: "news-received-the-postechian-fellowship-creative",
          title: '🏅 Received the POSTECHIAN Fellowship (Creative).',
          description: "",
          section: "News",},{id: "news-our-paper-accepted-at-iclr-2026-sparta-scalable-and-principled-benchmark-of-tree-structured-multi-hop-qa-over-text-and-tables",
          title: '🔥 Our Paper accepted at ICLR 2026: “SPARTA: Scalable and Principled Benchmark of...',
          description: "",
          section: "News",},{id: "news-our-paper-accepted-at-neurips-2026-hi-q-hierarchical-evidence-guided-query-refinement-for-multi-hop-question-answering",
          title: '🔥 Our Paper accepted at NeurIPS 2026: “Hi-Q: Hierarchical Evidence-guided Query Refinement for...',
          description: "",
          section: "News",},{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/juevn", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/jueun-kim-510377232", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=OlNKlb0AAAAJ", "_blank");
        },
      },{
        id: 'social-x',
        title: 'X',
        section: 'Socials',
        handler: () => {
          window.open("https://twitter.com/jueun_kim_", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
