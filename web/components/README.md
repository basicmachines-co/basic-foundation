# Basic Components

These components have been vendored into your project using Copier. They provide a set of reusable UI components built with JinjaX, Tailwind CSS, and Alpine.js.

## Setup

1. Ensure you have JinjaX installed in your project:

   ```
   pip install jinjax
   ```

2. In your FastAPI app, set up JinjaX:

   ```python
   from fastapi import FastAPI
   from jinjax import Jinja

   app = FastAPI()
   jinjax = Jinja(app, path="path/to/jinjax_components")
   ```

3. Make sure Tailwind CSS is properly configured in your project to scan the `jinjax_components` directory.

4. If not already included, add Alpine.js to your base template:
   ```html
   <script src="https://unpkg.com/alpinejs" defer></script>
   ```

## Usage

To use a component in your templates:

```jinja
<button variant="primary">Click me</button>

<Accordion>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>Yes. It adheres to the WAI-ARIA design pattern.</AccordionContent>
  </AccordionItem>
</Accordion>
```

Refer to individual component files for specific usage instructions and available props.

## Customization

Feel free to modify these components to fit your project's needs. Remember to update your Tailwind configuration if you make significant changes to class names.

## Updating

To update these components in the future, you can re-run the Copier command used to vendor them. Be cautious if you've made local modifications, as they may be overwritten.
