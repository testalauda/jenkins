o "hello world"
mkdir /hello
touch /hello/hello.txt
mkdir -p /test/test1
touch /test/test1/world.txt
echo "hello hello" > /hello/hello.txt
echo "world world" > /test/test1/world.txt
cp -r /hello/* $ALAUDACD_UPLOAD_DIR
echo "hello i'm coming where"
echo "test"
echo "test123"
