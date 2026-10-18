# Language catalogue and locale policy

Language profiles live in config/languages/. A profile defines editorial conventions and suggested regions; it does not certify that every inference model can write the language reliably. Regional settings must remain user-overridable.

## Available profiles

| ID | Display name | Region policy / notes |
|---|---|---|
| ml-IN | Malayalam (India) | Kerala default |
| en-IN | English (India) | India default |
| hi-IN | Hindi (India) | India default |
| ta-IN | Tamil (India) | Tamil Nadu default; override when needed |
| es | Spanish | Choose region for local news |
| ar | Arabic | Region selection needed; audiences span many countries |
| fr-FR | French (France) | France default; can override |
| bn | Bengali | Choose e.g. Bangladesh or West Bengal |
| pt-BR | Portuguese (Brazil) | Brazil default; Portugal/other regions need override |
| ru-RU | Russian | Russia default; can override |
| id-ID | Indonesian | Indonesia default |
| ur-PK | Urdu (Pakistan) | Pakistan default; script/region can override |
| de-DE | German (Germany) | Germany default; Austria/Switzerland need override |
| ja-JP | Japanese | Japan default |
| pcm-NG | Nigerian Pidgin | Nigeria default; spelling conventions need evaluation |
| fa-IR | Persian (Iran) | Iran default; Dari and Tajik are distinct locale/language needs |
| mr-IN | Marathi | Maharashtra default |
| vi-VN | Vietnamese | Vietnam default |
| te-IN | Telugu | Configure coverage for Andhra Pradesh and Telangana |
| tr-TR | Turkish | Türkiye default |
| ms-MY | Malay (Malaysia) | Malaysia default; “Malaysian” is a regional label, not a separate language |
| nl-NL | Dutch (Netherlands) | Netherlands default; Belgium needs override |
| as-IN | Assamese | Assam default |
| it-IT | Italian | Italy default; other Italian-speaking regions need override |
| or-IN | Odia | Odisha default; older sources may spell it Oriya |
| bih | Bihari language family | Placeholder only; choose Bhojpuri, Maithili, Magahi or another specific variety |
| raj | Rajasthani language group | Placeholder only; choose Marwari, Mewari, Dhundhari, Harauti or another variety |
| pa-IN | Punjabi (India) | Gurmukhi default; Shahmukhi/Pakistan needs explicit script/locale |
| bho-IN | Bhojpuri | Record preferred script where relevant |
| kn-IN | Kannada | Karnataka default |
| gu-IN | Gujarati | Gujarat default |

## Region is separate from language
Language does not uniquely determine geography. Bengali can target Bangladesh or West Bengal; English can target many countries; Arabic spans national news ecosystems. The bot should ask for a region when the default is ambiguous and always allow an override. Do not infer a user's physical location from language alone.

## Script and variety
- Urdu, Punjabi, Persian, Arabic and some language communities require attention to script/localization.
- Nigerian Pidgin has diverse writing practices; choose a consistent convention and test with native readers.
- Bihari and Rajasthani profiles are family/group placeholders. They must not be used for unattended publication until a variety is chosen.
- Bhojpuri is separate; a family-level Bihari selection must not silently claim Bhojpuri output.

## Quality gate
For every locale/model pair, maintain reviewed fixtures covering headlines, dates/units, attribution, technical terms, uncertainty, regional context and high-impact topics. Review fluency, factual fidelity, omissions and hallucinations. A profile alone does not satisfy this gate.
