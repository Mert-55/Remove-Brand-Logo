# Remove-Brand-Logo
Please Never use it to remove annoying brand logos from your pdf slides.

You only need python,
and this dependencies
```cmd
py -m pip install pillow PyMuPDF
```

Example Usage:
```cmd
python .\Documents\remove_brand_logo.py .\Downloads\Slides_VirtuellerCampus.pdf .\Downloads --offset_list "15" --rect_coords 0 750 100 800
```
