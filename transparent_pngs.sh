for img in img/*-kanji.jpg; do 
    magick "$img" -fuzz 50% -transparent white "${img%.jpg}.png"; 
done
